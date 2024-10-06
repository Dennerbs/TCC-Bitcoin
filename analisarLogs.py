import pandas as pd
from datetime import datetime
import re
from Graficos.negociacoes import plotar_negociacoes, plotar_evolucao_dinheiro

def ler_logs_arquivo(arquivo_log):
    with open(arquivo_log, 'r') as arquivo:
        logs = arquivo.readlines()
    return logs

def filtrar_logs(logs):
    logs_filtrados = [linha for linha in logs if "- INFO - log_" in linha]
    return logs_filtrados

def extrair_dados_logs(logs):
    dados_logs = {
        "log_compra": [],
        "log_venda": [],
        "log_saldo": [],
        "log_indicador": []
    }
    
    for log in logs:

        if "log_compra" in log:
            match = re.search(r"log_compra: ({.*})", log)
            if match:
                log_data = eval(match.group(1))
                dados_logs["log_compra"].append(log_data)
        elif "log_venda" in log:
            match = re.search(r"log_venda: ({.*})", log)
            if match:
                log_data = eval(match.group(1))
                dados_logs["log_venda"].append(log_data)
        elif "log_saldo" in log:
            match = re.search(r"log_saldo: ({.*})", log)
            if match:
                log_data = eval(match.group(1))
                dados_logs["log_saldo"].append(log_data)
        elif "log_indicador" in log:
            match = re.search(r"log_indicador: ({.*})", log)
            if match:
                log_data = eval(match.group(1))
                dados_logs["log_indicador"].append(log_data)
    
    return dados_logs

def extrair_dados_graficos(dados_logs):
    datas = []
    fechamento = []
    sinais_compra = {}
    sinais_venda = {}
    conteudo_grafico = []

    for log in dados_logs["log_saldo"]:
        datas.append(log['Data'])
        fechamento.append(log["valor_bitcoin"])

    for log in dados_logs["log_compra"]:
        indicador = log["indicador"]
        if indicador not in sinais_compra:
            sinais_compra[indicador] = {"x": [], "y": []}
        sinais_compra[indicador]["x"].append(log['Data'])
        sinais_compra[indicador]["y"].append(log["valor_bitcoin"])
        
    for log in dados_logs["log_venda"]:
        indicador = log["indicador"]
        if indicador not in sinais_venda:
            sinais_venda[indicador] = {"x": [], "y": []}
        sinais_venda[indicador]["x"].append(log['Data'])
        sinais_venda[indicador]["y"].append(log["valor_bitcoin"])
        
    for log in dados_logs["log_indicador"]:
        conteudo = log["conteudo_grafico"]
        conteudo_grafico.append(conteudo)
        
    valores = {
        "x": datas,
        "y": [log["saldo"] for log in dados_logs["log_saldo"]],
    }

    return datas, fechamento, sinais_compra, sinais_venda, valores, conteudo_grafico

def agrupar_propriedades(array):
    resultado = {}
    for obj in array:
        for chave, valor in obj.items():
            if chave in resultado:
                resultado[chave].append(valor)
            else:
                resultado[chave] = [valor]
    return resultado

def plotar_indicadores(conteudo_grafico, indicadores, datas, fechamento):
    dados_graficos = agrupar_propriedades(conteudo_grafico)
    dados_graficos['data'] = datas
    dados_graficos['fechamento'] = fechamento
    for indicador in indicadores:
        indicador.plotar_grafico(dados_graficos)
        
def analisar_logs(indicadores, arquivo_log ='trade_logs_TESTE.log', valor_total=100):

    logs = ler_logs_arquivo(arquivo_log)
    logs_filtrados = filtrar_logs(logs)
    dados_logs = extrair_dados_logs(logs_filtrados)
    datas, fechamento, sinais_compra, sinais_venda, valores, conteudo_grafico = extrair_dados_graficos(dados_logs)
    if indicadores : plotar_indicadores(conteudo_grafico, indicadores, datas, fechamento)
    plotar_negociacoes(datas, fechamento, sinais_compra, sinais_venda)

    plotar_evolucao_dinheiro(valores, valor_total, True, sinais_compra, pd.DataFrame({'date': datas, 'close': fechamento}))
    
#analisar_logs(None, 'trade_logs_TESTE.log', 100)