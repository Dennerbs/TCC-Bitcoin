from API.binance_api import get_dados_criptomoeda, get_linha, tempo_intervalo
from Utils.utils import calibrar_df_indicadores
import time
import pandas as pd

def trade(indicadores, intervalo='1h', simbolo = 'BTCUSDT'):
    sinais_compra = {indicador.nome_indicador: {'x':[], 'y':[]} for indicador in indicadores}
    sinais_venda = {indicador.nome_indicador: {'x':[], 'y':[]} for indicador in indicadores}
    valores = {'x':[], 'y':[]}
    
    df_inicial = get_dados_criptomoeda()
    
    calibrar_df_indicadores(indicadores, df_inicial = df_inicial)
    intervalo_em_segundo = tempo_intervalo(intervalo)
    
    time.sleep(intervalo_em_segundo)
    
    
    
    while True:
        saldo = 0
        # Obtém a linha de dados ao vivo
        linha = get_linha(intervalo, simbolo)
        
        for i, indicador in enumerate(indicadores):
            sinal = indicador.calcular_sinal(linha)
            
            if sinal == 'Vender' or indicador.get_stop(linha['close']):
                if indicador.get_estado():
                    indicador.set_estado(False)
                    valor_venda = indicador.get_quantidade_bitcoin() * linha['close']
                    indicador.set_valor_disponivel(valor_venda)
                    indicador.set_quantidade_vendas(valor_venda)
                    indicador.set_quantidade_bitcoin(0)
                    sinais_venda[indicador.nome_indicador]['x'].append(linha['date'])
                    sinais_venda[indicador.nome_indicador]['y'].append(linha['close'])
            elif sinal == 'Comprar':
                if not indicador.get_estado():
                    indicador.set_quantidade_compras()
                    indicador.set_estado(True)
                    btc_a_comprar = indicador.get_valor_disponivel() / linha['close']
                    indicador.set_quantidade_bitcoin(btc_a_comprar)
                    indicador.set_valor_disponivel(0)
                    sinais_compra[indicador.nome_indicador]['x'].append(linha['date'])
                    sinais_compra[indicador.nome_indicador]['y'].append(linha['close'])
            
            saldo += indicador.get_valor_disponivel() + indicador.get_quantidade_bitcoin() * linha['close']
        valores['x'].append(linha['date'])
        valores['y'].append(saldo)
        
        # Espera o próximo intervalo
        time.sleep(intervalo_em_segundo)