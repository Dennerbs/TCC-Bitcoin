from Simulacao.simulador import simulador
from analisarLogs import analisar_logs
from Utils.utils import get_df, ajustar_valores_porcentagem, get_indicadores, padronizar_df, limpar_df, definir_periodo_df
from Utils.Log import configurar_logger
from Indicadores.macd import MACD
from Indicadores.rsi import RSI
from Indicadores.volume import Volume
from Indicadores.superIndicador import SuperIndicador
from Operacao.operacao import trade
from API.binance_api import get_valores_minimos_operacao
import asyncio
from copy import copy
import logging
import os
import json
from dotenv import load_dotenv
load_dotenv()
with open('API/config.json') as f:
    json_config = json.load(f)
ambiente = os.getenv('AMBIENTE')
config = json_config[ambiente]
arquivo_log = config['arquivo_log']


def preparar_indicadores():
    volume = {
        "indicador": "Volume",
        "periodo": 125,
        "porcentagem_lucro_minimo_venda": 1.02, 
        "porcentagem_valor_total": 33, 
        "stop_loss": -2
    }
    rsi = {
        "indicador": "RSI",
        "periodo": 60,
        "topo": 67, 
        "baixa": 27,
        "porcentagem_lucro_minimo_venda": 1.02, 
        "porcentagem_valor_total": 33, 
        "stop_loss": -2
    }
    macd = {
        "indicador": "MACD",
        "periodo_curto": 13, 
        "periodo_longo": 26,
        "periodo_linha_sinal": 9,
        "porcentagem_lucro_minimo_venda": 1.02,
        "porcentagem_valor_total": 33, 
        "stop_loss": -2
    }
    #Indicadores
    indicadores = [volume, rsi, macd]
    
    return indicadores

def instanciar_indicadores(indicadores, valor_total):
    
    classe_indicador = {
        'MACD': MACD,
        'RSI': RSI,
        'Volume': Volume
    }
    
    instancias = []
    indicadores_solos = get_indicadores(indicadores)
    
    for indicador in indicadores_solos:
            nome_indicador = indicador['indicador']
            ClasseIndicador = classe_indicador[nome_indicador]
            atributos = copy(indicador)
            del atributos["indicador"]

            instancia = ClasseIndicador(valor_total=valor_total, **atributos)
            indicador['indicador'] = instancia

    for indicador in indicadores:
        if isinstance(indicador, list):
            instancias_sub_indicadores = []
            for sub_indicador in indicador:
                instancias_sub_indicadores.append(sub_indicador['indicador'])
            super_indicador = SuperIndicador(instancias_sub_indicadores, valor_total)
            instancias.append(super_indicador)
        else:
            instancias.append(indicador['indicador'])
    
    ajustar_valores_porcentagem(instancias)
    return instancias

def preparar_df(dataframe, periodo = '1min', filtro_datas = None):
    df = padronizar_df(dataframe)
    df = definir_periodo_df(df, periodo, filtro_datas)
    df = limpar_df(df)
    return df

def rodar_simulacao(filtro_datas, periodo= "1h", valor_total = 1000, arquivo_logs='trade_logs_SIMULACAO.log'):
    configurar_logger(arquivo_logs)
    df_original = get_df(2024)
    df = preparar_df(df_original, periodo=periodo, filtro_datas=filtro_datas)
    indicadores_preparados = preparar_indicadores()
    indicadores_prontos = instanciar_indicadores(indicadores_preparados, valor_total)
    simulador(df, indicadores_prontos, indicadores_preparados, valor_total)
    analisar_logs(indicadores_prontos, arquivo_logs, valor_total)

def rodar_ao_vivo(valor_total = 1000, periodo = '1m', calibracao_indicadores = 500):
    configurar_logger(arquivo_log)
    indicadores_preparados = preparar_indicadores()
    indicadores_prontos = instanciar_indicadores(indicadores_preparados, valor_total)
    log_inicial = {
        "valor_inicial": valor_total,
        "config_indicadores": indicadores_preparados
    }
    logging.info(f'log_inicial: {log_inicial}')
    asyncio.get_event_loop().run_until_complete(trade(indicadores_prontos,ambiente, periodo, calibracao_indicadores))
    
def plotar_graficos_operacao(valor_total = 1000):
    indicadores_preparados = preparar_indicadores()
    indicadores_prontos = instanciar_indicadores(indicadores_preparados, valor_total)
    analisar_logs(indicadores_prontos, arquivo_log, valor_total)
    
def main():
    # 2017-08-17 -> 2024-05-20
    # crescente: '2024-02-12','2024-05-12'
    # decrescente: '2024-03-13','2024-03-20'
    # macd 3h
    
    #Simulucao
    rodar_simulacao(['2023-10-06 17:15:00','2023-10-16 09:50:00'],'1min', 100)
    
    #Ao vivo
    #rodar_ao_vivo(100)
    
    #Plotar graficos do ao vivo
    #plotar_graficos_operacao(100)
    
    
main()







