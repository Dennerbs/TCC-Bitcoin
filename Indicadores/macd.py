from .indicador import Indicador
import pandas as pd
import matplotlib.pyplot as plt
import math
from matplotlib.dates import DateFormatter

class MACD(Indicador):
    def __init__(self, periodo_curto, periodo_longo, porcentagem_valor_total, valor_total, stop_loss, signal_window=9):
        super().__init__(porcentagem_valor_total, valor_total, stop_loss)
        self.periodo_curto = periodo_curto
        self.periodo_longo = periodo_longo
        self.signal_window = signal_window
        self.linha_curta = []
        self.linha_longa = []
        self.linha_macd = []


    def calcular_sinal(self, linha):
        self.set_linha_df(linha)
        self.calcular_macd_por_linha()
        self.tomar_decisao_macd_por_linha()

        sinais = self.df['decisao'].tolist()
        return sinais[-1]

    def calcular_macd(self):
        # Calcula as médias móveis exponenciais
        linha_curta = self.df['close'].ewm(span=self.periodo_curto, adjust=False).mean()
        linha_longa = self.df['close'].ewm(span=self.periodo_longo, adjust=False).mean()

        # Calcula a linha MACD
        self.df['MACD'] = linha_curta - linha_longa

        # Calcula a linha de sinal
        self.df['linha_macd'] = self.df['MACD'].ewm(span=self.signal_window, adjust=False).mean()

        return self.df

    def tomar_decisao_macd(self):
        self.df['decisao'] = 'Manter'

        for i in range(1, len(self.df)):
            if self.df['MACD'][i] > self.df['linha_macd'][i] and self.df['MACD'][i - 1] <= self.df['linha_macd'][i - 1]:
                self.df.at[i, 'decisao'] = 'Comprar'
            elif self.df['MACD'][i] < self.df['linha_macd'][i] and self.df['MACD'][i - 1] >= self.df['linha_macd'][i - 1]:
                self.df.at[i, 'decisao'] = 'Vender'
                
        return self.df
    
    #Funcoes por linha
    def calcular_macd_por_linha(self):
        index_nova_linha = len(self.df) - 1
        valor_fechamento_atual = self.df['close'].iloc[index_nova_linha]
        
        if index_nova_linha <= self.periodo_curto:
            self.linha_curta.append(valor_fechamento_atual)
            self.linha_longa.append(valor_fechamento_atual)
            self.linha_macd.append(0)
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
        
        
    def tomar_decisao_macd_por_linha(self):
        decisao = 'Manter'
        # Verifica se tem linha suficiente para fazer analise por linha
        index_nova_linha = len(self.df) - 1
        if index_nova_linha <= self.periodo_curto:
            # Se não, retorna decisao de `Manter`
            self.df.loc[index_nova_linha, 'decisao'] = decisao
            return
        
        
        macd_atual = self.df['MACD'].iloc[index_nova_linha]
        macd_anterior = self.df['MACD'].iloc[index_nova_linha - 1]
        linha_macd_atual = self.df['linha_macd'].iloc[index_nova_linha]
        linha_macd_anterior = self.df['linha_macd'].iloc[index_nova_linha - 1]
        
        # Verifica se houve cruzamento do MACD com a linha de sinal
        if macd_atual > linha_macd_atual and macd_anterior <= linha_macd_anterior:
            # MACD cruzou acima da linha de sinal, oportunidade de compra
            decisao = 'Comprar'
        elif macd_atual < linha_macd_atual and macd_anterior >= linha_macd_anterior:
            # MACD cruzou abaixo da linha de sinal, oportunidade de venda
            decisao = 'Vender'
        
        self.df.loc[index_nova_linha, 'decisao'] = decisao
    
    def graficoMacd(self):
        
        plt.figure(figsize=(10, 6))
        #plt.plot(df['date'], df['close'], label='Preço', color='black')
        #plt.plot(df['date'], df['dif'], label='diferenca', color='black')
        plt.plot(self.df['date'], self.df['MACD'], label='MACD', color='blue')
        plt.plot(self.df['date'], self.df['linha_macd'], label='linha MACD', color='red')
        
        espacamento = math.ceil(len(self.df['date']) / 10)
        plt.xticks(self.df['date'][::espacamento], rotation=20)


        plt.title('MACD Indicator')
        plt.xlabel('Data')
        #plt.ylabel('Preço')
        plt.legend()
        plt.show()
