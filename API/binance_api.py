from binance.client import Client
import pandas as pd
import pytz
import os
import websockets
import asyncio
import json
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY_BINACE")
api_secret = os.getenv("API_SECRET_BINACE")

client = Client(api_key, api_secret)

def comprar_ativo(quantidade, symbol = 'BTCBRL'):
    try:
        quantidade_formatada = f"{quantidade:.8f}".rstrip('0').rstrip('.')
        order = client.create_order(
            symbol=symbol,
            side=Client.SIDE_BUY,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantidade_formatada
        )
        return order
    except Exception as e:
        print(f"Erro ao executar a ordem de compra: {e}")

def vender_ativo(quantidade, symbol = 'BTCBRL'):
    try:
        quantidade_formatada = f"{quantidade:.8f}".rstrip('0').rstrip('.')
        order = client.create_order(
            symbol=symbol,
            side=Client.SIDE_SELL,
            type=Client.ORDER_TYPE_MARKET,
            quantity=quantidade_formatada
        )
        return order
    except Exception as e:
        print(f"Erro ao executar a ordem de venda: {e}")
        
def get_valor_minimo_operacao(symbol):
    info = client.get_symbol_info(symbol)
    filtro_notional = next(filter(lambda x: x['filterType'] == 'NOTIONAL', info['filters']))
    return float(filtro_notional['minNotional'])

def calcular_valor_taxa_em_real(commission, avg_price):
    valor_taxa_em_real = commission * avg_price
    return valor_taxa_em_real

def tratar_ordem(ordem):
    fills = ordem['fills']
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
    
    valor_taxa_em_real = calcular_valor_taxa_em_real(total_commission, avg_price)
    
    resultado = {
        'valor_ativo': avg_price,
        'quantidade_ativo': total_qty,
        'valor_operacao': avg_price * total_qty,
        'taxa': total_commission,
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
    

async def get_dados_bitcoin_websocket(intervalo='1h'):
    url = f"wss://stream.binance.com:9443/ws/btcusdt@kline_{intervalo}"

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
                        print(f"Erro durante o recebimento de dados: {e}")
                        break
        except (websockets.exceptions.ConnectionClosedError, asyncio.TimeoutError) as e:
            print(f"Erro de conexão ou tempo limite: {e}")
            print("Tentando reconectar em 5 segundos...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Erro inesperado: {e}")
            break


