
from datetime import datetime, timedelta
import pandas as pd
from API.binance_api import get_valores_minimos_operacao

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
            
            
def formatar_log_compra_venda(ciclo, nome_indicador, sinal, quantidade_bitcoin, dados_ordem):
    return {
                "ciclo": ciclo,
                "indicador": nome_indicador,
                "valor_operacao": dados_ordem['valor_operacao'],
                "taxa_operacao": dados_ordem['taxa_em_real'],
                "valor_bitcoin": dados_ordem['valor_ativo'],
                "quantidade_ordem": quantidade_bitcoin,
                "quantidade_efetivada": dados_ordem['quantidade_ativo'],
                "sinal": sinal
            }
    
def formatar_log_indicador(indicador, valor_close):
    return {
                "nome_indicador" : indicador.nome_indicador,
                "Saldo indicador": indicador.get_valor_disponivel() + indicador.get_quantidade_bitcoin() * valor_close,
                "Lucro": indicador.calcular_lucro(),
                "Lucro por operacao": indicador.calcular_lucro_por_operacao(),
                "Somatorio ganhos": indicador.get_somatorio_ganhos(),
                "Somatorio perdas": indicador.get_somatorio_perdas(),
                "Ganhos por operacao": indicador.calcular_ganho_por_venda(),
                "Perdas por operacao": indicador.calcular_perda_por_venda(),
                "Somatorio Taxas de operacao": indicador.get_somatorio_taxas_transacao(),
                "Taxas por operacao": indicador.calcular_taxa_por_operacao()
            }
def ajustar_quantidade_ativo(quantidade_desejada, incremento_minimo):
    quantidade_final = round(quantidade_desejada / incremento_minimo) * incremento_minimo
    return f"{quantidade_final:.10f}".rstrip('0')

def autorizar_compra(indicador, preco_ativo, ativo):
    valor_minimo_negociacao, quantidade_minima = get_valores_minimos_operacao(ativo)
    valor_disponivel = indicador.get_valor_disponivel()
    quantidade_desejada = valor_disponivel / preco_ativo
    quantidade_a_comprar = ajustar_quantidade_ativo(quantidade_desejada, quantidade_minima)
    valor_total_esperado = float(quantidade_a_comprar) * preco_ativo
    if valor_total_esperado > valor_minimo_negociacao:
        return quantidade_a_comprar, valor_disponivel
    else:
        return None
    
def autorizar_venda(indicador, preco_ativo, ativar_stop_loss, ativo):
    valor_minimo_negociacao, quantidade_minima = get_valores_minimos_operacao(ativo)
    quantidade_ativo_disponivel = indicador.get_quantidade_bitcoin()
    quantidade_a_vender = ajustar_quantidade_ativo(quantidade_ativo_disponivel, quantidade_minima)
    valor_total_esperado = float(quantidade_a_vender) * preco_ativo
    if valor_total_esperado > valor_minimo_negociacao:
        lucro_potencial = calcular_lucro_potencial(valor_total_esperado)
        lucro_minimo = indicador.get_lucro_minimo_venda()
        if ativar_stop_loss or lucro_potencial > lucro_minimo:
            return quantidade_a_vender, quantidade_ativo_disponivel
    return None

def calcular_lucro_potencial(valor_total_esperado, taxa_operacao_binance = 0.001):
    taxa_transacao = valor_total_esperado * taxa_operacao_binance
    return valor_total_esperado - taxa_transacao
    
def calcular_dias(datas):
    formato_data = "%Y-%m-%d"
    data_inicial = datetime.strptime(datas[0], formato_data)
    data_final = datetime.strptime(datas[1], formato_data)
    diferenca_dias = (data_final - data_inicial).days
    return diferenca_dias

def get_df_15_minutos(ano, colunas_desejadas):
    return pd.read_csv(f'./Dados/{ano}_15min.csv',usecols=colunas_desejadas)

def get_df(ano):
    return pd.read_csv(f'./Dados/BTC-{ano}min.csv')

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
    