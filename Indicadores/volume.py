import pandas as pd
import mplfinance as mpf 
from .indicador import Indicador

class Volume(Indicador):
    def __init__(self, periodo, valor_total, porcentagem_lucro_minimo_venda, porcentagem_valor_total, stop_loss):
        super().__init__(porcentagem_lucro_minimo_venda, porcentagem_valor_total, valor_total, stop_loss, self.__class__.__name__)
        self.periodo = periodo 
        self.soma_volume = 0
        
    def calcular_sinal(self, linha):
        if not self.df.empty and linha['date'] == self.df['date'].iloc[-1]:
            return self.df.at[len(self.df) - 1, 'decisao']
        self.set_linha_df(linha)
        if len(self.df) < self.periodo:
            self.df.at[len(self.df) - 1, 'obv'] = 0
            return 'Manter'

        index_nova_linha = len(self.df) - 1
        obv = self.calcular_obv(index_nova_linha)
        self.df.at[index_nova_linha, 'obv'] = obv
        valores = self.df[['close', 'obv']].iloc[-self.periodo:]
        soma_diferenca_preco = valores['close'].diff().iloc[1:].sum() 
        soma_diferenca_obv = valores['obv'].diff().iloc[1:].sum() 

        self.df.at[index_nova_linha, 'decisao'] = self.tomar_decisao_volume(soma_diferenca_preco, soma_diferenca_obv)
        return self.df.at[index_nova_linha, 'decisao']
        
    def calcular_obv(self, index):
        volume_atual = self.df.at[index, 'volume']
        preco_atual = self.df.at[index, 'close']
        preco_anterior = self.df.at[index - 1, 'close']
        obv_anterior = self.df.at[index - 1, 'obv']
        if preco_atual > preco_anterior:
            return obv_anterior + volume_atual
        elif preco_atual < preco_anterior:
            return obv_anterior - volume_atual
        else:
            return obv_anterior

    def tomar_decisao_volume(self, preco, obv):
        preco_subindo = preco > 0
        obv_subindo = obv > 0
        if not preco_subindo and obv_subindo :
            return "Comprar"  
        elif preco_subindo and not obv_subindo:
            return "Vender"  
        else:
            return "Manter"
        
    
    def plotar_grafico(self):
        self.df['date'] = pd.to_datetime(self.df['date'])

        self.df = self.df.rename(columns={
            'date': 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'volume': 'Volume'
        })
        self.df.set_index('Date', inplace=True)
        
        df = self.df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        mpf.plot(df, type='line', volume=True, title='Gráfico com Volume', style='yahoo')
