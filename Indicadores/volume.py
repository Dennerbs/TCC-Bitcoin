from .indicador import Indicador
import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import math
from matplotlib.dates import DateFormatter

class Volume(Indicador):
    def __init__(self, porcentagem_valor_total, valor_total, stop_loss):
        super().__init__(porcentagem_valor_total, valor_total, stop_loss)
        self.soma_volume = 0
        
    def calcular_sinal(self, linha):
        self.setLinhaDf(linha)
        index_nova_linha = len(self.df) - 1
        volume = linha['Volume BTC']
        self.soma_volume += volume
        media_volume = self.soma_volume / len(self.df['Volume BTC'])
        self.df.loc[index_nova_linha, 'media_volume'] = media_volume
        
        return self.tomar_decisao_volume(volume, media_volume)
        
        
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

        