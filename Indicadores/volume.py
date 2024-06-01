from .indicador import Indicador
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import math
from matplotlib.dates import DateFormatter

class Volume(Indicador):
    def __init__(self, valor_total, porcentagem_valor_total, stop_loss):
        super().__init__(porcentagem_valor_total, valor_total, stop_loss, self.__class__.__name__)
        self.soma_volume = 0
        
    def calcular_sinal(self, linha):
        if len(self.df) > 0 and linha['date'] == self.df['date'].iloc[-1]:
            return self.df.at[len(self.df) - 1, 'decisao']
        self.set_linha_df(linha)
        index_nova_linha = len(self.df) - 1
        volume = linha['Volume BTC']
        self.soma_volume += volume
        media_volume = self.soma_volume / len(self.df['Volume BTC'])
        self.df.loc[index_nova_linha, 'media_volume'] = media_volume
        self.df.loc[index_nova_linha, 'decisao'] = self.tomar_decisao_volume(volume, media_volume)
        
        return self.df.at[len(self.df) - 1, 'decisao']
        
        
    def tomar_decisao_volume(self, volume_atual, media_volume):
        if volume_atual < media_volume:
            return "Vender"  
        elif volume_atual > media_volume:
            return "Comprar"  
        else:
            return "Manter"
    
    def graficoVolume(self):
        self.df['date'] = pd.to_datetime(self.df['date'])

        self.df = self.df.rename(columns={
            'date': 'Date',
            'open': 'Open',
            'high': 'High',
            'low': 'Low',
            'close': 'Close',
            'Volume BTC': 'Volume'
        })
        self.df.set_index('Date', inplace=True)
        
        df = self.df[['Open', 'High', 'Low', 'Close', 'Volume']]
        
        mpf.plot(df, type='line', volume=True, title='Gráfico com Volume', style='yahoo')

        