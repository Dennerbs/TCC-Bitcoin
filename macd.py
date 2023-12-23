import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter


def calcular_macd(df, periodo_curto=12, periodo_longo=26, signal_window=9):
    # Calcula as médias móveis exponenciais
    linha_curta = df['close'].ewm(span=periodo_curto, adjust=False).mean()
    linha_longa = df['close'].ewm(span=periodo_longo, adjust=False).mean()

    # Calcula a linha MACD
    df['MACD'] = linha_curta - linha_longa

    # Calcula a linha de sinal
    df['linha_macd'] = df['MACD'].ewm(span=signal_window, adjust=False).mean()
    

    return df


def graficoMacd(df,periodo):
    periodos = {'dia': "%Y-%m-%d", 'hora': "%Y-%m-%d %H:%M:%S"}
    plt.figure(figsize=(10, 6))
    #plt.plot(df['date'], df['close'], label='Preço', color='black')
    #plt.plot(df['date'], df['dif'], label='diferenca', color='black')
    plt.plot(df['date'], df['MACD'], label='MACD', color='blue')
    plt.plot(df['date'], df['linha_macd'], label='linha MACD', color='red')
    
    date_format = DateFormatter(periodos[periodo])
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gcf().autofmt_xdate()


    plt.title('MACD Indicator')
    plt.xlabel('Data')
    #plt.ylabel('Preço')
    plt.legend()
    plt.show()


def tomar_decisao_macd(df):

    df['decisao'] = 'Manter'
    
    for i, row in df.iterrows():
        # macd = row['MACD']
        # linha_macd = row['linha_macd']

        # diferenca = macd - linha_macd
        # porcentagem_diferenca = (diferenca / abs(linha_macd)) * 100 if linha_macd != 0 else 0

        # if macd < linha_macd and porcentagem_diferenca > porc_compra:
        #     #print(f'Compra | {data} | {porcentagem_diferenca} > {porc_compra}')
        #     df.at[i, 'decisao'] = 'Comprar'
        # elif porcentagem_diferenca > porc_venda:
        #     #print(f'Venda | {data} | {porcentagem_diferenca} > {porc_venda}')
        #     df.at[i, 'decisao'] = 'Vender'
            
        # Detecta os cruzamentos das linhas MACD e de sinal
    
        if df['MACD'][i] > df['linha_macd'][i] and df['MACD'][i - 1] <= df['linha_macd'][i - 1]:
           df.at[i, 'decisao'] = 'Comprar'
        elif df['MACD'][i] < df['linha_macd'][i] and df['MACD'][i - 1] >= df['linha_macd'][i - 1]:
            df.at[i, 'decisao'] = 'Vender'
    return df
      
            
            
 