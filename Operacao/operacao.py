from API.binance_api import get_dados_criptomoeda, get_linha, tempo_intervalo, get_dados_bitcoin_websocket
from Utils.utils import calibrar_df_indicadores, get_data_hora_agora
import time
import pandas as Timestamp
import json
import asyncio

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

async def trade(indicadores, valor_total, intervalo='1h', simbolo='BTCUSDT'):
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

    await asyncio.sleep(intervalo_em_segundo)
    contador = 0

    while True:
        contador += 1
        saldo = 0
        total_taxas = 0
        linha = await get_dados_bitcoin_websocket(intervalo)
        
        for indicador in indicadores:
            sinal = indicador.calcular_sinal(linha)
            
            parar_perda = indicador.get_stop(linha['close'])
            vender_bitcoin = sinal == 'Vender' or parar_perda
            if vender_bitcoin and indicador.get_estado():
                valor_venda = indicador.get_quantidade_bitcoin() * linha['close']
                taxa_transacao = valor_venda * 0.001
                lucro_potencial = valor_venda - taxa_transacao
                valor_ultima_compra = indicador.get_valor_ultima_compra()
                if parar_perda or (sinal == 'Vender' and lucro_potencial > valor_ultima_compra):
                    total_taxas += taxa_transacao
                    indicador.set_estado(False)
                    quantidade_bitcoin = indicador.get_quantidade_bitcoin()
                    valor_venda = quantidade_bitcoin * linha['close']
                    indicador.set_valor_disponivel(lucro_potencial)
                    indicador.set_quantidade_vendas(lucro_potencial)
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
                        "valor_venda": lucro_potencial,
                    }
                    salvar_log(log_venda, 'log_venda')
            elif sinal == 'Comprar':
                if not indicador.get_estado():
                    indicador.set_quantidade_compras()
                    indicador.set_estado(True)
                    valor_disponivel = indicador.get_valor_disponivel()
                    taxa_transacao = valor_disponivel * 0.001
                    valor_final = valor_disponivel - taxa_transacao
                    btc_a_comprar =  valor_final / linha['close']
                    indicador.set_quantidade_bitcoin(btc_a_comprar)
                    indicador.set_valor_disponivel(0)
                    total_taxas += taxa_transacao
                    sinais_compra[indicador.nome_indicador]['x'].append(linha['date'])
                    sinais_compra[indicador.nome_indicador]['y'].append(linha['close'])
                    log_compra = {
                        "Data": get_data_hora_agora(),
                        "ciclo": contador,
                        "indicador": indicador.nome_indicador,
                        "sinal": sinal,
                        "quantidade_comprada_bitcoin": btc_a_comprar,
                        "valor_bitcoin": linha['close'],
                        "valor_compra": valor_final,
                    }
                    salvar_log(log_compra, 'log_compra')

            saldo += indicador.get_valor_disponivel() + indicador.get_quantidade_bitcoin() * linha['close']
        
        log_saldo = {
                "Data": get_data_hora_agora(),
                "ciclo": contador,
                "saldo": saldo,
                "valor_bitcoin": linha['close'],
                "total_taxas:": total_taxas
            }
        salvar_log(log_saldo, 'log_saldo')
        valores['x'].append(linha['date'])
        valores['y'].append(saldo)
        
