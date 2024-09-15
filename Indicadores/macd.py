from .indicador import Indicador
import pandas as pd
import matplotlib.pyplot as plt
import math
from matplotlib.dates import DateFormatter

class MACD(Indicador):
    def __init__(self, periodo_curto, periodo_longo, valor_total, porcentagem_lucro_minimo_venda, porcentagem_valor_total, stop_loss, signal_window=9):
        super().__init__(porcentagem_lucro_minimo_venda, porcentagem_valor_total, valor_total, stop_loss, self.__class__.__name__)
        self.periodo_curto = periodo_curto
        self.periodo_longo = periodo_longo
        self.signal_window = signal_window
        self.linha_curta = []
        self.linha_longa = []
        self.linha_macd = []
        self.histograma = []
        self.sequencia_histograma_positiva = []
        self.sequencia_histograma_negativa = []

    def calcular_sinal(self, linha):
        if len(self.df) > 0 and linha['date'] == self.df['date'].iloc[-1]:
            return self.df['decisao'].iloc[-1]
            
        self.set_linha_df(linha)
        self.calcular_macd()
        self.tomar_decisao_macd()

        return self.df['decisao'].iloc[-1]

    def calcular_macd(self):
        index_nova_linha = len(self.df) - 1
        valor_fechamento_atual = self.df['close'].iloc[index_nova_linha]
        
        if index_nova_linha <= self.periodo_curto:
            self.linha_curta.append(valor_fechamento_atual)
            self.linha_longa.append(valor_fechamento_atual)
            self.linha_macd.append(0)
            self.histograma.append(0)
            self.sequencia_histograma_positiva.append(0)
            self.sequencia_histograma_negativa.append(0)
            return
        
        nova_linha_curta = valor_fechamento_atual * (2 / (self.periodo_curto + 1)) + \
                                self.linha_curta[-1] * (1 - (2 / (self.periodo_curto + 1)))
        nova_linha_longa = valor_fechamento_atual * (2 / (self.periodo_longo + 1)) + \
                                self.linha_longa[-1] * (1 - (2 / (self.periodo_longo + 1)))

        self.linha_curta.append(nova_linha_curta)
        self.linha_longa.append(nova_linha_longa)

        self.df.loc[index_nova_linha, 'MACD'] = nova_linha_curta - nova_linha_longa
        
        linha_macd = self.df['MACD'].iloc[index_nova_linha] * (2 / (self.signal_window + 1)) + \
                                                    self.linha_macd[-1] * (1 - (2 / (self.signal_window + 1)))
        self.linha_macd.append(linha_macd)

        self.df.loc[index_nova_linha, 'linha_macd'] = self.linha_macd[-1]
        
        histograma_atual = self.df['MACD'].iloc[index_nova_linha] - self.linha_macd[-1]

        preco_atual = self.df.at[index_nova_linha, 'close']
        preco_anterior = self.df.at[index_nova_linha - 1, 'close']
        if preco_atual > preco_anterior:
            valor = histograma_atual
            self.sequencia_histograma_positiva.append(valor)

        elif preco_atual < preco_anterior:
            valor = histograma_atual
            self.sequencia_histograma_negativa.append(valor)

        self.histograma.append(histograma_atual)


    def tomar_decisao_macd(self):
        decisao = 'Manter'
        index_nova_linha = len(self.df) - 1
        if index_nova_linha <= self.periodo_curto:
            self.df.loc[index_nova_linha, 'decisao'] = decisao
            return
        
        sequencia_histograma_negativa = self.sequencia_histograma_negativa[-self.periodo_curto:]
        sequencia_histograma_positiva = self.sequencia_histograma_positiva[-self.periodo_curto:]
        histograma_atual = self.histograma[-1]
        macd_atual = self.df['MACD'].iloc[index_nova_linha]
        linha_macd_atual = self.df['linha_macd'].iloc[index_nova_linha]
        
        media_positiva = sum(sequencia_histograma_positiva)/self.periodo_curto
        media_negativa = sum(sequencia_histograma_negativa)/self.periodo_curto

        if macd_atual > linha_macd_atual and histograma_atual > media_positiva:
            decisao = 'Comprar'
        elif macd_atual < linha_macd_atual and histograma_atual > media_negativa:
            decisao = 'Vender'
        
        self.df.loc[index_nova_linha, 'decisao'] = decisao

    def plotar_grafico(self):
        plt.figure(figsize=(10, 6))
        plt.plot(self.df['date'], self.df['MACD'], label='MACD', color='blue')
        plt.plot(self.df['date'], self.df['linha_macd'], label='Linha MACD', color='red')
        
        espacamento = math.ceil(len(self.df['date']) / 10)
        plt.xticks(self.df['date'][::espacamento], rotation=20)

        plt.title('MACD')
        plt.xlabel('Data')
        plt.legend()
        plt.show()
