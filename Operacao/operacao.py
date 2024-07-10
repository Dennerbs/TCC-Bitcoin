from API.binance_api import get_dados_criptomoeda, get_linha, tempo_intervalo
from Utils.utils import calibrar_df_indicadores, get_data_hora_agora
import time
import pandas as Timestamp
import json
def custom_serializer(obj):
    if isinstance(obj, Timestamp):
        return obj.isoformat()
    raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

def salvar_log(log, tipo_log):
    nome_arquivo = 'trade_logs.json'
    try:
        with open(nome_arquivo, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {'log_inicial': [], 'log_compra': [], 'log_venda': [], 'log_saldo': []}

    if tipo_log == 'log_inicial':
        data[tipo_log] = log
    else:
        data[tipo_log].append(log)

    with open(nome_arquivo, 'w') as file:
        json.dump(data, file, indent=4)

def trade(indicadores, valor_total, intervalo='1h', simbolo='BTCUSDT'):
    sinais_compra = {indicador.nome_indicador: {'x': [], 'y': []} for indicador in indicadores}
    sinais_venda = {indicador.nome_indicador: {'x': [], 'y': []} for indicador in indicadores}
    valores = {'x': [], 'y': []}
    
    df_inicial = get_dados_criptomoeda()
    calibrar_df_indicadores(indicadores, df_inicial=df_inicial)
    intervalo_em_segundo = tempo_intervalo(intervalo)

    log_inicial = {
        "inicio": get_data_hora_agora(),
        "valor_inicial": valor_total
    }
    salvar_log(log_inicial, 'log_inicial')

    time.sleep(intervalo_em_segundo)
    contador = 0

    while True:
        contador += 1
        saldo = 0
        linha = get_linha(intervalo, simbolo)
        
        for indicador in indicadores:
            sinal = indicador.calcular_sinal(linha)
            
            if sinal == 'Vender' or indicador.get_stop(linha['close']):
                if indicador.get_estado():
                    indicador.set_estado(False)
                    quantidade_bitcoin = indicador.get_quantidade_bitcoin()
                    valor_venda = quantidade_bitcoin * linha['close']
                    indicador.set_valor_disponivel(valor_venda)
                    indicador.set_quantidade_vendas(valor_venda)
                    indicador.set_quantidade_bitcoin(0)
                    sinais_venda[indicador.nome_indicador]['x'].append(linha['date'])
                    sinais_venda[indicador.nome_indicador]['y'].append(linha['close'])
                    log_venda = {
                        "Data": get_data_hora_agora(),
                        "ciclo": contador,
                        "indicador": indicador.nome_indicador,
                        "sinal": sinal,
                        "quantidade_vendida_bitcoin": quantidade_bitcoin,
                        "valor_bitcoin": linha['close'],
                        "valor_venda": valor_venda,
                    }
                    salvar_log(log_venda, 'log_venda')
            elif sinal == 'Comprar':
                if not indicador.get_estado():
                    indicador.set_quantidade_compras()
                    indicador.set_estado(True)
                    valor_disponivel = indicador.get_valor_disponivel()
                    btc_a_comprar = valor_disponivel / linha['close']
                    indicador.set_quantidade_bitcoin(btc_a_comprar)
                    indicador.set_valor_disponivel(0)
                    sinais_compra[indicador.nome_indicador]['x'].append(linha['date'])
                    sinais_compra[indicador.nome_indicador]['y'].append(linha['close'])
                    log_compra = {
                        "Data": get_data_hora_agora(),
                        "ciclo": contador,
                        "indicador": indicador.nome_indicador,
                        "sinal": sinal,
                        "quantidade_comprada_bitcoin": btc_a_comprar,
                        "valor_bitcoin": linha['close'],
                        "valor_compra": valor_disponivel,
                    }
                    salvar_log(log_compra, 'log_compra')

            saldo += indicador.get_valor_disponivel() + indicador.get_quantidade_bitcoin() * linha['close']
        log_saldo = {
                "Data": get_data_hora_agora(),
                "ciclo": contador,
                "saldo": saldo
            }
        salvar_log(log_saldo, 'log_saldo')
        valores['x'].append(linha['date'])
        valores['y'].append(saldo)
        
        time.sleep(intervalo_em_segundo)
