from Simulacao.simulador import simulador
from Utils.utils import get_df, transformar_minutos_em_dia, get_super_df, criar_df_15_minutos, salvar_df_para_csv, get_df_15_minutos, ajustar_valores_porcentagem, get_indicadores
from Indicadores.macd import MACD
from Indicadores.rsi import RSI
from Indicadores.volume import Volume
from Indicadores.superIndicador import SuperIndicador
from Graficos.negociacoes import plotar_negociacoes, plotar_evolucao_dinheiro
from copy import copy


def preparar_indicadores():
    volume = {
        "indicador": "Volume",
        "porcentagem_valor_total": 20, 
        "stop_loss": -5
    }
    rsi = {
        "indicador": "RSI",
        "periodo": 12,
        "topo": 50, 
        "baixa": 30, 
        "porcentagem_valor_total": 20, 
        "stop_loss": -5
    }
    macd = {
        "indicador": "MACD",
        "periodo_curto": 6, 
        "periodo_longo": 13,
        "porcentagem_valor_total": 20, 
        "stop_loss": -5
    }
    #Indicadores
    indicadores = [macd,rsi, [volume, rsi]]
    
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

def main():
    #df = get_super_df()
    df = get_df(2021)
    #colunas_desejadas = ['date','close']
    #dfDias = get_df_15_minutos(2021, colunas_desejadas)
    # print(df)
    dfDias = transformar_minutos_em_dia(df)

    #dfDias = criar_df_15_minutos(df)
    #print(len(dfDias))
    #salvar_df_para_csv(dfDias, '2021_15min.csv')
    #dfM = dfDias[35719:]
    dfM = dfDias
    valorTotal = 1000
    indicadores_preparados = preparar_indicadores()
    indicadores_prontos = instanciar_indicadores(indicadores_preparados, valorTotal)
    saldo, sinais_compra,  sinais_venda, valores = simulador(dfM, indicadores_prontos, len(dfM))
    

    plotar_negociacoes(dfM['date'],dfM['close'],sinais_compra, sinais_venda)
    plotar_evolucao_dinheiro(valores, valorTotal, False, sinais_compra, dfM)
    
    
main()






