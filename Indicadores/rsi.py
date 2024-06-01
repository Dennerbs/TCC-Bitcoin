from .indicador import Indicador
import pandas as pd
import matplotlib.pyplot as plt
import math
from matplotlib.dates import DateFormatter

class RSI(Indicador):
    def __init__(self, periodo, topo, baixa, valor_total, porcentagem_valor_total, stop_loss):
        super().__init__(porcentagem_valor_total, valor_total, stop_loss, self.__class__.__name__)
        self.periodo = periodo
        self.topo = topo
        self.baixa = baixa
        

    def calcular_sinal(self, linha):
        if len(self.df) > 0 and linha['date'] == self.df['date'].iloc[-1]:
            return self.df.at[len(self.df) - 1, 'decisao']
        self.set_linha_df(linha)
        self.calcular_diferenca_por_linha()
        self.calcular_ganho_perda_por_linha()
        self.calcular_media_ganho_perda_por_linha(self.periodo)
        self.calcular_rsi_por_linha()
        self.tomar_decisao_RSI_por_linha()

        return self.df.at[len(self.df) - 1, 'decisao']

        # sinais = []
        # for rsi_valor in self.df['rsi']:
        #     decisao = self.analisar_decisao_RSI(rsi_valor)
        #     sinais.append(decisao)

        #return sinais[-1]

    def calcular_diferenca(self):
        df = self.df.copy()
        df['diferenca'] = df['close'].diff()
        return df

    def calcular_ganho_perda(self):
        self.df['ganho'] = 0
        self.df['perda'] = 0

        for i in range(1, len(self.df)):
            diferenca = self.df.at[i, 'diferenca']
            if diferenca > 0:
                self.df.at[i, 'ganho'] = diferenca
            else:
                self.df.at[i, 'perda'] = abs(diferenca)

        return self.df

    def calcular_media_ganho_perda(self, periodo):
        self.df['media_ganho'] = 0
        self.df['media_perda'] = 0

        for i in range(1, len(self.df)):
            if i < periodo:
                # Calcula a média simples das primeiras 'i' linhas
                media_ganho = self.df['ganho'][:i].mean()
                media_perda = self.df['perda'][:i].mean()
            else:
                # Calcula a média ponderada a partir do período definido
                media_ganho = ((self.df['media_ganho'][i - 1] * (periodo - 1)) + self.df['ganho'][i]) / periodo
                media_perda = ((self.df['media_perda'][i - 1] * (periodo - 1)) + self.df['perda'][i]) / periodo

            self.df.at[i, 'media_ganho'] = media_ganho
            self.df.at[i, 'media_perda'] = media_perda

        return self.df

    def calcular_rsi(self):
        for i in range(len(self.df)):
            media_ganho = self.df.at[i, 'media_ganho']
            media_perda = self.df.at[i, 'media_perda']

            if media_perda == 0:
                rs = 0
            else:
                rs = media_ganho / media_perda

            rsi = 100 - (100 / (1 + rs))
            self.df.at[i, 'rsi'] = rsi

        return self.df

    def analisar_decisao_RSI(self, rsi_valor):
        if rsi_valor > self.topo:
            return "Vender"  
        elif rsi_valor < self.baixa:
            return "Comprar"  
        else:
            return "Manter"
        
    def graficoRSI(self):
        self.df['rsi'] = self.df['rsi'].astype(float) 

        plt.figure(figsize=(10, 5))
        plt.plot(self.df['date'], self.df['rsi'], label='RSI', color='blue')
        plt.axhline(self.topo, color='r', linestyle='--', label=f'Topo ({self.topo})')
        plt.axhline(self.baixa, color='g', linestyle='--', label=f'Baixa ({self.baixa})')
        
        plt.title('Gráfico de RSI')
        plt.xlabel('Data')
        plt.ylabel('RSI')
        
        espacamento = math.ceil(len(self.df['date']) / 10)
        plt.xticks(self.df['date'][::espacamento], rotation=20)
        
        plt.legend()
        plt.show()
        
        
        
        #Funcoes por linha
    def calcular_diferenca_por_linha(self):
        index_nova_linha = len(self.df) - 1
        close_atual = self.df['close'].iloc[index_nova_linha]
        if index_nova_linha < 1:
            self.df.loc[index_nova_linha, 'diferenca'] = close_atual
            return
        close_anterior = self.df['close'].iloc[index_nova_linha - 1]
        self.df.loc[index_nova_linha, 'diferenca'] = close_atual - close_anterior
        return self.df

    def calcular_ganho_perda_por_linha(self):
        index_nova_linha = len(self.df) - 1
        self.df.loc[index_nova_linha, 'ganho'] = 0
        self.df.loc[index_nova_linha, 'perda'] = 0
        
        diferenca = self.df.at[index_nova_linha, 'diferenca']
        
        if diferenca > 0:
            self.df.loc[index_nova_linha, 'ganho'] = diferenca
        else:
            self.df.loc[index_nova_linha, 'perda'] = abs(diferenca)

        return self.df

    def calcular_media_ganho_perda_por_linha(self, periodo):
        # Verifica a última linha adicionada
        index_nova_linha = len(self.df) - 1

        # Verifica se o período é maior do que o número total de linhas
        if len(self.df) < periodo:
            # Calcula as médias simples das primeiras linhas
            media_ganho = self.df['ganho'].mean()
            media_perda = self.df['perda'].mean()
            self.df.at[index_nova_linha, 'media_ganho'] = media_ganho
            self.df.at[index_nova_linha, 'media_perda'] = media_perda
        else:
            # Se não, calcula as médias móveis usando a última linha adicionada
            media_ganho_anterior = self.df.at[index_nova_linha - 1, 'media_ganho']
            media_perda_anterior = self.df.at[index_nova_linha - 1, 'media_perda']

            # Atualiza as médias móveis com base na última linha adicionada
            media_ganho_nova = ((media_ganho_anterior * (periodo - 1)) + self.df.at[index_nova_linha, 'ganho']) / periodo
            media_perda_nova = ((media_perda_anterior * (periodo - 1)) + self.df.at[index_nova_linha, 'perda']) / periodo

            # Atualiza as colunas de médias no DataFrame
            self.df.at[index_nova_linha, 'media_ganho'] = media_ganho_nova
            self.df.at[index_nova_linha, 'media_perda'] = media_perda_nova

        return self.df

    def calcular_rsi_por_linha(self):
        # Obter o índice da última linha
        index_nova_linha = len(self.df) - 1

        # Obter as médias de ganho e perda da última linha
        media_ganho = self.df.at[index_nova_linha, 'media_ganho']
        media_perda = self.df.at[index_nova_linha, 'media_perda']

        # Calcular o RSI para a última linha
        if media_perda == 0:
            rs = 0  # Se não houver perda, o RS é zero
        else:
            rs = media_ganho / media_perda

        # Calcular o RSI
        rsi = 100 - (100 / (1 + rs))

        # Atualizar a última linha com o RSI calculado
        self.df.at[index_nova_linha, 'rsi'] = rsi

        return self.df
    
    def tomar_decisao_RSI_por_linha(self):
        index_nova_linha = len(self.df) - 1
        rsi_valor = self.df.at[index_nova_linha, 'rsi']
        self.df.at[index_nova_linha, 'decisao'] = self.analisar_decisao_RSI(rsi_valor)

