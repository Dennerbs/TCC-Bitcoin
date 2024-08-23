from binance.client import Client
import pandas as pd
import pytz
import os
import websockets
import asyncio
import json
import logging
from dotenv import load_dotenv

load_dotenv()

with open('API/config.json') as f:
    json_config = json.load(f)
ambiente = os.getenv('AMBIENTE')
config = json_config[ambiente]

api_key = os.getenv(config['api_key'])
api_secret = os.getenv(config['api_secret'])
testnet = config['testnet']

client = Client(api_key, api_secret, testnet=testnet)

def comprar_ativo(quantidade, quantidade_minima, preco, symbol = 'BTCBRL'):
    try:
        print("comprar_ativo")
        print("quantidade")
        print(quantidade)
        quantidade_formatada = ajustar_quantidade_ativo(quantidade, quantidade_minima)
        print("quantidade_formatada")
        print(quantidade_formatada)
        order = client.create_order(
            symbol=symbol,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantidade_formatada
        )
        return order
    except Exception as e:
        logging.error(f"Erro ao executar a ordem de compra: {e} | {quantidade_formatada} | {preco}")

def vender_ativo(quantidade, quantidade_minima, preco, symbol = 'BTCBRL'):
    try:
        print("vender_ativo")
        print("quantidade")
        print(quantidade)
        quantidade_formatada = ajustar_quantidade_ativo(quantidade, quantidade_minima)
        print("quantidade_formatada")
        print(quantidade_formatada)
        order = client.create_order(
            symbol=symbol,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantidade_formatada
        )
        return order
    except Exception as e:
        logging.error(f"Erro ao executar a ordem de venda: {e} | {quantidade_formatada} | {preco}")
        
def get_valores_minimos_operacao(symbol):
    try:
        info = client.get_symbol_info(symbol)
        filtros = {filtro['filterType']: filtro for filtro in info['filters']}
        
        valor_minimo = float(filtros['NOTIONAL']['minNotional'])
        quantidade_minima = float(filtros['LOT_SIZE']['minQty'])
        
        return valor_minimo, quantidade_minima
    except KeyError as e:
        raise ValueError(f"Filtro {e} não encontrado para o símbolo {symbol}")
    except Exception as e:
        raise RuntimeError(f"Erro ao obter informações para o símbolo {symbol}: {e}")

def calcular_valor_taxa_em_real(taxa, ativo_da_taxa, preco_ativo):
    if ativo_da_taxa == 'BRL':
        valor_taxa_em_real = taxa
    else: 
        valor_taxa_em_real = taxa * preco_ativo
    return valor_taxa_em_real

def calcular_valor_taxa_em_real_teste(valor_operacao, ativo_da_taxa, preco_ativo):
    taxa = 0
    taxa_operacao_binance = 0.001
    valor_taxa_em_real = float(valor_operacao) * taxa_operacao_binance
    if ativo_da_taxa == 'BRL':
        taxa = valor_taxa_em_real
    else: 
        taxa = valor_taxa_em_real / preco_ativo
        
    return taxa, valor_taxa_em_real


def tratar_ordem(ordem):
    fills = ordem['fills']
    valor_operacao = ordem['cummulativeQuoteQty']
    total_price = 0.0
    total_qty = 0.0
    total_commission = 0.0
    commission_asset = fills[0]['commissionAsset']
    
    for fill in fills:
        total_price += float(fill['price']) * float(fill['qty'])
        total_qty += float(fill['qty'])
        total_commission += float(fill['commission'])
    
    # calcula o preço médio
    avg_price = total_price / total_qty
    if testnet : 
        total_commission, valor_taxa_em_real = calcular_valor_taxa_em_real_teste(valor_operacao, commission_asset, avg_price)
    else:
        valor_taxa_em_real = calcular_valor_taxa_em_real(total_commission, commission_asset, avg_price)
    
    resultado = {
        'valor_ativo': avg_price,
        'quantidade_ativo': f"{total_qty:.8f}".rstrip('0'),
        'valor_operacao': valor_operacao,
        'taxa': f"{total_commission:.8f}".rstrip('0'),
        'moeda_cobranca_taxa': commission_asset,
        'taxa_em_real': valor_taxa_em_real
    }
    
    return resultado

# Obter dados de mercado ao vivo
def get_dados_criptomoeda(intervalo='1h', simbolo='BTCBRL'):
    klines = client.get_klines(symbol=simbolo, interval=intervalo)
    
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'quote_asset_volume', 'number_of_trades', 
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    timezone = pytz.timezone('America/Campo_Grande')
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(timezone)
    
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    
    df.rename(columns={'timestamp': 'date'}, inplace=True)

    return df

def get_linha(intervalo, simbolo):
    df = get_dados_criptomoeda(intervalo=intervalo, simbolo=simbolo)
    return df.iloc[-1]

def tempo_intervalo(intervalo):
    unit = intervalo[-1]
    if unit == 'm':
        return int(intervalo[:-1]) * 60
    elif unit == 'h':
        return int(intervalo[:-1]) * 3600
    elif unit == 'd':
        return int(intervalo[:-1]) * 86400
    elif unit == 'w':
        return int(intervalo[:-1]) * 604800
    elif unit == 'M':
        return int(intervalo[:-1]) * 2592000
    

async def get_dados_bitcoin_websocket(ativo='btcbrl',intervalo='1h'):
    url = config['websocket'].format(ativo=ativo, intervalo=intervalo)
    while True:
        try:
            async with websockets.connect(url) as ws:
                while True:
                    try:
                        response = await ws.recv()
                        data = json.loads(response)

                        kline = data['k']
                        if kline['x']:
                            new_row = {
                                'date': pd.to_datetime(kline['t'], unit='ms'),
                                'open': float(kline['o']),
                                'high': float(kline['h']),
                                'low': float(kline['l']),
                                'close': float(kline['c']),
                                'volume': float(kline['v'])
                            }

                            timezone = pytz.timezone('America/Campo_Grande')
                            new_row['date'] = new_row['date'].tz_localize('UTC').tz_convert(timezone)

                            return new_row
                    except Exception as e:
                        logging.error(f"Erro durante o recebimento de dados: {e}")
                        break
        except (websockets.exceptions.ConnectionClosedError, asyncio.TimeoutError) as e:
            logging.error(f"Erro de conexão ou tempo limite: {e}")
            logging.error("Tentando reconectar em 5 segundos...")
            await asyncio.sleep(5)
        except Exception as e:
            logging.error(f"Erro inesperado: {e}")
            break
        
def ajustar_quantidade_ativo(quantidade_desejada, incremento_minimo):
    quantidade_final = (quantidade_desejada // incremento_minimo) * incremento_minimo
    return f"{quantidade_final:.10f}".rstrip('0')




