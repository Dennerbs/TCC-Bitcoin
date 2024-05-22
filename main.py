from Simulacao.simulador import simulador
from Utils.utils import criarDf, transformar_minutos_em_dia, criarSuperDf, convert_to_15min_intervals, salvar_df_para_csv, criarDfMinutos
from Indicadores.macd import MACD
from Indicadores.rsi import RSI
from Indicadores.volume import Volume
from Graficos.negociacoes import plot_negociacoes, graficoEvolucaoDinheiro

#df = criarSuperDf()
df = criarDf(2021)
#colunas_desejadas = ['date','close']
#dfDias = criarDfMinutos(2021, colunas_desejadas)
# print(df)
dfDias = transformar_minutos_em_dia(df)

#dfDias = convert_to_15min_intervals(df)
#print(len(dfDias))
#salvar_df_para_csv(dfDias, '2021_15min.csv')
#dfM = dfDias[35719:]
dfM = dfDias
valorTotal = 1000
volume = Volume(20, valorTotal, -5)
macd = MACD(6, 13, 40, valorTotal,-5)
rsi = RSI(12,50,30,40,valorTotal,-5)
indicadores = [volume, macd, rsi]
saldo,sinais_compra,  sinais_venda, valores = simulador(dfM, indicadores, len(dfM))
rsi.graficoRSI()
macd.graficoMacd()
volume.graficoVolume()

plot_negociacoes(dfM['date'],dfM['close'],sinais_compra, sinais_venda)
graficoEvolucaoDinheiro(valores, valorTotal, True, sinais_compra, dfM)