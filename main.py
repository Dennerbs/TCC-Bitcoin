from Simulacao.simulador import simulador
from Utils.utils import get_df, transformar_minutos_em_dia, get_super_df, criar_df_15_minutos, salvar_df_para_csv, get_df_15_minutos
from Indicadores.macd import MACD
from Indicadores.rsi import RSI
from Indicadores.volume import Volume
from Indicadores.superIndicador import SuperIndicador
from Graficos.negociacoes import plotar_negociacoes, plotar_evolucao_dinheiro

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
volume = Volume(20, valorTotal, -5)
macd = MACD(6, 13, 40, valorTotal,-5)
rsi = RSI(12,50,30,40,valorTotal,-5)
indicadores_combinados = SuperIndicador([volume, rsi], valorTotal)

indicadores = [indicadores_combinados, macd]
saldo, sinais_compra,  sinais_venda, valores = simulador(dfM, indicadores, len(dfM))
rsi.graficoRSI()
macd.graficoMacd()
volume.graficoVolume()

plotar_negociacoes(dfM['date'],dfM['close'],sinais_compra, sinais_venda)
plotar_evolucao_dinheiro(valores, valorTotal, False, sinais_compra, dfM)