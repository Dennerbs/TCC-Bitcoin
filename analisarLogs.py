import pandas as pd
from datetime import datetime
import json
import re
import glob
from Graficos.negociacoes import plotar_negociacoes, plotar_evolucao_dinheiro, plotar_drawdown
from Utils.utils import calcular_buy_and_hold, calcular_desvio_padrao
def ler_logs_arquivo(arquivo_log):
    arquivos_log = glob.glob(f"{arquivo_log}*")
    
    arquivos_log.sort(key=lambda x: int(re.search(r'\.log(?:\.(\d+))?$', x).group(1) or 0), reverse=True)
    
    logs_totais = []

    for arquivo_log in arquivos_log:
        with open(arquivo_log, 'r') as arquivo:
            logs_totais.extend(arquivo.readlines())
    
    return logs_totais


def filtrar_logs(logs):
    logs_filtrados = [linha for linha in logs if "- INFO - log_" in linha]
    return logs_filtrados

def extrair_dados_logs(logs):
    tipos_logs = ["log_compra", "log_venda", "log_saldo", "log_indicador"]
    dados_logs = {tipo: [] for tipo in tipos_logs}

    for log in logs:
        for tipo in tipos_logs:
            if tipo in log:
                match = re.search(rf"{tipo}: (\{{.*\}})", log)
                if match:
                    try:
                        log_data = eval(match.group(1)) 
                        dados_logs[tipo].append(log_data)
                    except json.JSONDecodeError as e:
                        print(f"Erro : {e}")

    formatar_datas(dados_logs)
    return dados_logs

def formatar_datas(logs):
    def formatar_data(data_str):
        data = datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S,%f')
        return data.strftime('%Y-%m-%d %H:%M:%S')

    for chave in logs:
        for log in logs[chave]:
            log['Data'] = formatar_data(log['Data'])
                
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
            sinais_venda[indicador] = {"x": [], "y": []}
        sinais_compra[indicador]["x"].append(log['Data'])
        sinais_compra[indicador]["y"].append(log["valor_bitcoin"])
        
    for log in dados_logs["log_venda"]:
        indicador = log["indicador"]
        if indicador not in sinais_venda:
            sinais_venda[indicador] = {"x": [], "y": []}
            sinais_compra[indicador] = {"x": [], "y": []}
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

def contar_negociacoes(sinais_compra, sinais_venda):
    contagem = {}
    
    for indicador in sinais_compra:
        qtd_compras = len(sinais_compra[indicador]["x"])
        qtd_vendas = len(sinais_venda[indicador]["x"])
        
        contagem[indicador] = {
            "compras": qtd_compras,
            "vendas": qtd_vendas
        }
    
    return contagem
 
def analisar_logs(indicadores, arquivo_log ='trade_logs_TESTE.log', valor_total=100):

    logs = ler_logs_arquivo(arquivo_log)
    logs_filtrados = filtrar_logs(logs)
    dados_logs = extrair_dados_logs(logs_filtrados)
    datas, fechamento, sinais_compra, sinais_venda, valores, conteudo_grafico = extrair_dados_graficos(dados_logs)
    if indicadores : plotar_indicadores(conteudo_grafico, indicadores, datas, fechamento)
    plotar_negociacoes(datas, fechamento, sinais_compra, sinais_venda)
    valores_bh = calcular_buy_and_hold(pd.DataFrame({'date': datas, 'close': fechamento}), valor_total, sinais_compra)
    plotar_evolucao_dinheiro(valores, valores_bh)
    plotar_drawdown(valores, valores_bh)
    
    print(f'Saldo final buy and hold: {valores_bh[1][-1]}')
    print(f'Desvio padrão Investimento: {calcular_desvio_padrao(valores["y"])}')
    print(f'Desvio buy and hold: {calcular_desvio_padrao(valores_bh[1])}')
    print(contar_negociacoes(sinais_compra, sinais_venda))
    
    
    
#analisar_logs(None, 'trade_logs_TESTE.log', 100)