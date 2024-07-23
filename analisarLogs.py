import json
import pandas as pd
from datetime import datetime

from Graficos.negociacoes import plotar_negociacoes, plotar_evolucao_dinheiro


with open('teste23-07.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)
dados_logs = json_data

def converter_datas(logs, date_key="Data"):
    for log in logs:
        log[date_key] = datetime.strptime(log[date_key], "%d/%m/%Y | %H:%M:%S")

converter_datas(dados_logs["log_compra"])
converter_datas(dados_logs["log_venda"])
converter_datas(dados_logs["log_saldo"])


def extrair_dados_log(dados_logs):
    datas = [log["Data"] for log in dados_logs["log_saldo"]]
    fechamento = [log["valor_bitcoin"] for log in dados_logs["log_saldo"]]
    sinais_compra = {
            "Volume": {
                "x": [],
                "y": [],
            },
            "RSI": {
                "x": [],
                "y": [],
            },
            "MACD": {
                "x": [],
                "y": [],
            }
        }
    sinais_venda = {
            "Volume": {
                "x": [],
                "y": [],
            },
            "RSI": {
                "x": [],
                "y": [],
            },
            "MACD": {
                "x": [],
                "y": [],
            }
        }
    for log in dados_logs["log_compra"]:
        sinais_compra[log["indicador"]]["x"].append(log["Data"])
        sinais_compra[log["indicador"]]["y"].append(log["valor_bitcoin"])
        
    for log in dados_logs["log_venda"]:
        sinais_venda[log["indicador"]]["x"].append(log["Data"])
        sinais_venda[log["indicador"]]["y"].append(log["valor_bitcoin"])

    valores = {
        "x": [log["Data"] for log in dados_logs["log_saldo"]],
        "y": [log["saldo"] for log in dados_logs["log_saldo"]],
    }

    return datas, fechamento, sinais_compra, sinais_venda, valores

datas, fechamento, sinais_compra, sinais_venda, valores = extrair_dados_log(dados_logs) 

plotar_negociacoes(datas, fechamento, sinais_compra, sinais_venda)
plotar_evolucao_dinheiro(valores, 1000, True, sinais_compra, pd.DataFrame({'date': datas, 'close': fechamento}))