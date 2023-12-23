
from datetime import datetime
import pandas as pd

def criarSuperDf():
    #Cria super dataframe com dados bitcoin
    anos = [2017, 2018, 2019, 2020, 2021]

    dfAll = pd.DataFrame()

    for ano in anos:
        arquivo_csv = f'../Arqs/teste/BTC-{ano}min.csv'
        df = pd.read_csv(arquivo_csv)
        if df.iloc[0]['date'] > df.iloc[-1]['date']:
            df = df[::-1].reset_index(drop=True)
        dfAll = pd.concat([dfAll, df], ignore_index=True)
    return dfAll

def criaDf(ano):
    return pd.read_csv(f'../Arqs/teste/BTC-{ano}min.csv')

#funcao df  em dias
def transformar_minutos_em_dia(df):

    #coloca o df na ordem crescente a partir da data
    if df.iloc[0]['date'] > df.iloc[-1]['date']:
        df = df[::-1].reset_index(drop=True)

    df['date'] = pd.to_datetime(df['date'])

    # Filtra as linhas onde a hora é 00:00:00
    filtered_df = df[df['date'].dt.time == pd.Timestamp('00:00:00').time()]
    #Altera o index do df
    filtered_df.reset_index(drop=True, inplace=True)
    return filtered_df

def transformar_minutos_em_horas(df):
    
    #coloca o df na ordem crescente a partir da data
    if df.iloc[0]['date'] > df.iloc[-1]['date']:
        df = df[::-1].reset_index(drop=True)
        
    # Convertendo a coluna 'date' para o tipo datetime
    df['date'] = pd.to_datetime(df['date'])

    # Arredondando para a hora mais próxima
    df['hour'] = df['date'].dt.floor('H')

    # Agrupando por hora e selecionando a primeira linha de cada grupo
    df_por_hora = df.groupby('hour').first().reset_index()
    
    return df_por_hora

def formata_datas(df):
    df['formattedDate'] = "";
    for i in range(len(df)):
        df.at[i, 'formattedDate'] = datetime.utcfromtimestamp(df.at[i,'unix']).strftime('%d-%m-%y')
    return df