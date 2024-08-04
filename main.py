from Simulacao.simulador import simulador
from Utils.utils import get_df, ajustar_valores_porcentagem, get_indicadores, padronizar_df, limpar_df, definir_periodo_df, calcular_dias
from Indicadores.macd import MACD
from Indicadores.rsi import RSI
from Indicadores.volume import Volume
from Indicadores.superIndicador import SuperIndicador
from Graficos.negociacoes import plotar_negociacoes, plotar_evolucao_dinheiro
from Operacao.operacao import trade
import asyncio
from copy import copy


def preparar_indicadores():
    volume = {
        "indicador": "Volume",
        "periodo": 125,
        "lucro_minimo_venda": 1.02, 
        "porcentagem_valor_total": 20, 
        "stop_loss": -2
    }
    rsi = {
        "indicador": "RSI",
        "periodo": 12,
        "topo": 67, 
        "baixa": 27,
        "lucro_minimo_venda": 1.02, 
        "porcentagem_valor_total": 20, 
        "stop_loss": -5
    }
    macd = {
        "indicador": "MACD",
        "periodo_curto": 6, 
        "periodo_longo": 13,
        "lucro_minimo_venda": 1.02,
        "porcentagem_valor_total": 20, 
        "stop_loss": -5
    }
    #Indicadores
    indicadores = [volume, macd, rsi]
    
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
    
def main():
    # 2017-08-17 -> 2024-05-20
    # crescente: '2024-02-12','2024-05-12'
    # decrescente: '2024-03-13','2024-03-20'
    # macd 3h
    # df_original = get_df(2024)
    # filtro_datas=['2024-03-13','2024-03-20']
    # df = preparar_df(df_original, periodo='1min', filtro_datas=filtro_datas)
    # valorTotal = 100
    # indicadores_preparados = preparar_indicadores()
    # indicadores_prontos = instanciar_indicadores(indicadores_preparados, valorTotal)
    # saldo, sinais_compra,  sinais_venda, valores = simulador(df, indicadores_prontos, calcular_dias(filtro_datas))
    
    # plotar_negociacoes(df['date'],df['close'],sinais_compra, sinais_venda)
    # plotar_evolucao_dinheiro(valores, valorTotal, False, sinais_compra, df)
    
    valorTotal = 1000
    indicadores_preparados = preparar_indicadores()
    indicadores_prontos = instanciar_indicadores(indicadores_preparados, valorTotal)
    #trade(indicadores_prontos,valorTotal, '1m')
    asyncio.get_event_loop().run_until_complete(trade(indicadores_prontos,valorTotal, '1m'))
    # plotar_negociacoes(indicadores_prontos[0].df['date'],indicadores_prontos[0].df['close'],sinais_compra, sinais_venda)
    # plotar_evolucao_dinheiro(valores, valorTotal, False, sinais_compra, indicadores_prontos[0].df)
    
    
main()







