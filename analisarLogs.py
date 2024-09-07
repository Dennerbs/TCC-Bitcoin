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
        data_str = log.split('- I')[0].strip()
        data_formatada = datetime.strptime(data_str, "%Y-%m-%d %H:%M:%S,%f")

        if "log_compra" in log:
            match = re.search(r"log_compra: ({.*})", log)
            if match:
                log_data = eval(match.group(1))
                log_data["Data"] = data_formatada
                dados_logs["log_compra"].append(log_data)
        elif "log_venda" in log:
            match = re.search(r"log_venda: ({.*})", log)
            if match:
                log_data = eval(match.group(1))
                log_data["Data"] = data_formatada
                dados_logs["log_venda"].append(log_data)
        elif "log_saldo" in log:
            match = re.search(r"log_saldo: ({.*})", log)
            if match:
                log_data = eval(match.group(1))
                log_data["Data"] = data_formatada
                dados_logs["log_saldo"].append(log_data)
        elif "log_indicador" in log:
            match = re.search(r"log_indicador: ({.*})", log)
            if match:
                log_data = eval(match.group(1))
                log_data["Data"] = data_formatada
                dados_logs["log_indicador"].append(log_data)
    
    return dados_logs

def extrair_dados_graficos(dados_logs):
    datas = []
    fechamento = []
    sinais_compra = {}
    sinais_venda = {}

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

    valores = {
        "x": datas,
        "y": [log["saldo"] for log in dados_logs["log_saldo"]],
    }

    return datas, fechamento, sinais_compra, sinais_venda, valores

logs = ler_logs_arquivo('trade_logs_TESTE.log')
logs_filtrados = filtrar_logs(logs)
dados_logs = extrair_dados_logs(logs_filtrados)
datas, fechamento, sinais_compra, sinais_venda, valores = extrair_dados_graficos(dados_logs)
plotar_negociacoes(datas, fechamento, sinais_compra, sinais_venda)

plotar_evolucao_dinheiro(valores, 59, True, sinais_compra, pd.DataFrame({'date': datas, 'close': fechamento}))