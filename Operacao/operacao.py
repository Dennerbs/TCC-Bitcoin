from API.binance_api import get_dados_criptomoeda, tempo_intervalo, get_dados_bitcoin_websocket
from Utils.utils import calibrar_df_indicadores, get_data_hora_agora
import json
import os
import asyncio

def salvar_log(log, tipo_log):
    base_nome_arquivo = 'trade_logs'
    extensao_arquivo = '.json'
    limite_linhas = 5000

    numero_arquivo = 0
    while True:
        nome_arquivo = f'{base_nome_arquivo}_{numero_arquivo}{extensao_arquivo}'
        if not os.path.exists(nome_arquivo):
            break
        with open(nome_arquivo, 'r') as file:
            data = json.load(file)
            total_linhas = sum(len(data[key]) for key in data)
            if total_linhas < limite_linhas:
                break
        numero_arquivo += 1

    try:
        with open(nome_arquivo, 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {'log_inicial': [], 'log_compra': [], 'log_venda': [], 'log_saldo': []}

    if tipo_log == 'log_inicial':
        data[tipo_log] = log
    else:
        data[tipo_log].append(log)

    with open(nome_arquivo, 'w') as file:
        json.dump(data, file, indent=4)

async def trade(indicadores, valor_total, intervalo='1h', simbolo='BTCUSDT'):
    df_inicial = get_dados_criptomoeda(intervalo)
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
        print(f'Ciclo: {contador}')
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
                lucro_minimo = valor_ultima_compra * indicador.get_lucro_minimo_venda()
                if parar_perda or (sinal == 'Vender' and lucro_potencial > lucro_minimo):
                    indicador.set_estado(False)
                    quantidade_bitcoin = indicador.get_quantidade_bitcoin()
                    valor_venda = quantidade_bitcoin * linha['close']
                    indicador.set_valor_disponivel(lucro_potencial)
                    indicador.set_quantidade_vendas(lucro_potencial)
                    indicador.set_somatorio_taxas(taxa_transacao)
                    indicador.set_quantidade_bitcoin(0)
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
                    indicador.set_somatorio_taxas(taxa_transacao)
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
            total_taxas += indicador.get_somatorio_taxas_transacao()
        
        log_saldo = {
                "Data": get_data_hora_agora(),
                "ciclo": contador,
                "saldo": saldo,
                "total_taxas:": total_taxas,
                "volume": linha['volume'],
                "valor_bitcoin": linha['close']
            }
        salvar_log(log_saldo, 'log_saldo')
        
