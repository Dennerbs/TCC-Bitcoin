
from datetime import datetime, timedelta
import pandas as pd


def padronizar_df(df):
    if 'Volume BTC' in df.columns:
        df = df.rename(columns={'Volume BTC': 'volume'})
    return df[['date', 'open', 'high', 'low', 'close', 'volume']]

def limpar_df(df):
    linhas_antes = len(df)
    #Remover linhas com valores null
    df_limpo = df.dropna(axis=0)
    #Remover linhas com valores 0
    df_limpo = df_limpo[(df_limpo != 0).all(axis=1)]
    linhas_depois = len(df_limpo)
    print(f'Saúde df = {(linhas_depois  / linhas_antes )*100 }%')
    return df_limpo

import pandas as pd

def definir_periodo_df(df, periodo, filtro_datas):

    df['date'] = pd.to_datetime(df['date'])
    
    if filtro_datas:
        data_inicial, data_final = filtro_datas
        data_inicial = pd.to_datetime(data_inicial)
        data_final = pd.to_datetime(data_final) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
        df_filtrado = df.loc[(df['date'] >= data_inicial) & (df['date'] <= data_final)]
    else:
        df_filtrado = df

    df_filtrado.set_index('date', inplace=True)
    df_agrupado = df_filtrado.resample(periodo).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    })

    df_agrupado.reset_index(inplace=True)
    return df_agrupado

def calibrar_df_indicadores(indicadores, df_inicial, periodo_df = 500):
    df = df_inicial[:periodo_df]
    for indice, linha in df.iterrows():
        print("indice: ", indice)
        for i, indicador in enumerate(indicadores):
            indicador.calcular_sinal(linha)

def get_super_df():
    #Cria super dataframe com dados bitcoin
    anos = [2017, 2018, 2019, 2020, 2021]

    dfAll = pd.DataFrame()

    for ano in anos:
        arquivo_csv = f'./Dados/BTC-{ano}min.csv'
        df = pd.read_csv(arquivo_csv)
        if df.iloc[0]['date'] > df.iloc[-1]['date']:
            df = df[::-1].reset_index(drop=True)
        dfAll = pd.concat([dfAll, df], ignore_index=True)
    return dfAll

def get_df_15_minutos(ano, colunas_desejadas):
    
    return pd.read_csv(f'./Dados/{ano}_15min.csv',usecols=colunas_desejadas)

def get_df(ano):
    return pd.read_csv(f'./Dados/BTC-{ano}min.csv')

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

def criar_df_15_minutos(df):
    df15Min = pd.DataFrame(columns=['unix','date','symbol','open','high','low','close','volume','Volume USD'])
    df15Min = df15Min._append(df.iloc[0], ignore_index=True)
    df['date'] = pd.to_datetime(df['date'])

    # Ordenar o DataFrame pela coluna 'date'
    df = df.sort_values(by='date')
    
    # Pegar o valor da primeira linha da coluna 'date'
    current_date = df.iloc[0]['date']
    
    # Loop para iterar sobre as linhas do DataFrame
    index = df.iloc[0].name
    while index > 14:
        print('index: ', index)
        # Somar 14 minutos à data atual
        current_date += timedelta(minutes=14)
        # Encontrar a próxima linha onde a coluna 'date' seja maior que a data atual
        next_row = df[df['date'] > current_date].iloc[0]

        index_next_row = next_row.name
        
        # Adicionar a próxima linha ao DataFrame
        df15Min = df15Min._append(next_row, ignore_index=True)
        
        # Atualizar a data atual para a data da próxima linha
        current_date = next_row['date']
        print('index_next_row: ', index_next_row)
        index = index_next_row

    return df15Min

def salvar_df_para_csv(dataframe, nome_arquivo):

    dataframe.to_csv(nome_arquivo, index=False)
    print(f"DataFrame salvo com sucesso no arquivo {nome_arquivo}")
    
def get_indicadores(indicadores):
    indicadores_sozinhos = []

    for indicador in indicadores:
        if isinstance(indicador, list):
            for sub_indicador in indicador:
                if sub_indicador not in indicadores_sozinhos:
                    indicadores_sozinhos.append(sub_indicador)
        else:
            if indicador not in indicadores_sozinhos:
                    indicadores_sozinhos.append(indicador)
    return indicadores_sozinhos

def ajustar_para_100_porcento(porcentagens):
        total = sum(porcentagens)
        
        fator = 100 / total
        porcentagens_ajustadas = [round(porcentagem * fator) for porcentagem in porcentagens]
        
        diferenca = 100 - sum(porcentagens_ajustadas)
        if diferenca != 0:
            indice_maior_porcentagem = porcentagens_ajustadas.index(max(porcentagens_ajustadas))
            porcentagens_ajustadas[indice_maior_porcentagem] += diferenca
        
        return porcentagens_ajustadas
    
def ajustar_valores_porcentagem(indicadores):
    
    porcentagens = [indicador.get_porcentagem_valor_total()  for indicador in indicadores]
    porcentagens_ajustadas = ajustar_para_100_porcento(porcentagens)
    cc = 0
    for indicador in indicadores:
        indicador.set_porcentagem_valor_total(porcentagens_ajustadas[cc])
        cc += 1
    