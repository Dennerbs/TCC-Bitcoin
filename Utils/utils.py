
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

def get_df_15_minutos(ano, colunas_desejadas):
    return pd.read_csv(f'./Dados/{ano}_15min.csv',usecols=colunas_desejadas)

def get_df(ano):
    return pd.read_csv(f'./Dados/BTC-{ano}min.csv')

def get_data_hora_agora():
    return datetime.now().strftime("%d/%m/%Y | %H:%M:%S")
 

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
    