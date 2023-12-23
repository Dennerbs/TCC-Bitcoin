# Imports
# Link dataset : https://www.kaggle.com/datasets/prasoonkottarathil/btcinusd/
import pandas as pd
import numpy as np

import matplotlib.dates as mdates
from matplotlib.dates import drange
from utils import criaDf, criarSuperDf, transformar_minutos_em_dia, formata_datas, transformar_minutos_em_horas
from simulacao import graficoEvolucaoDinheiro, simulador
from rsi import calcular_diferenca, calcular_ganho_perda, calcular_media_ganho_perda, calcular_rsi, graficoRSI, imprimir_rsi, tomar_decisao_RSI
from macd import calcular_macd, graficoMacd, tomar_decisao_macd
#criar superDF
df = criarSuperDf()
#criar df ano especifico
#df = criaDf(2021)

##################################################
#print(df.loc[100])
#dfMin = transformar_minutos_em_horas(df)
dfDias = transformar_minutos_em_dia(df)
# dfDias = formata_datas(dfDias)


def indiceForcaRelativa(df, periodo, topo, baixa, stop_loss):

    df = calcular_diferenca(df)
    df = calcular_ganho_perda(df)
    df = calcular_media_ganho_perda(df, periodo)
    df = calcular_rsi(df)

    df = imprimir_rsi(df, topo, baixa)
    simulador(df, 1000,stop_loss, df.shape[0])
    #graficoRSI(df,topo, baixa)
    
def macd(df, periodo_curto, periodo_longo, stop_loss):
    df = calcular_macd(df, periodo_curto, periodo_longo)
    df = tomar_decisao_macd(df)
    simulador(df,1000,stop_loss,df.shape[0])
    #graficoMacd(df, "dia")
    
    
macd(dfDias, 12, 26,5)
#indiceForcaRelativa(dfDias, 12, 80, 50, 5)
print("dfDias['date'][0]")
print(dfDias['date'][0])
print("dfDias['date'].iloc[-1]")
print(dfDias['date'].iloc[-1])


