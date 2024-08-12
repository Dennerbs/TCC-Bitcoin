from .indicador import Indicador
import matplotlib.pyplot as plt
import math
import numpy as np

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
        self.calcular_diferenca()
        self.calcular_ganho_perda()
        self.calcular_media_ganho_perda(self.periodo)
        self.calcular_rsi()
        self.tomar_decisao_RSI()

        return self.df.at[len(self.df) - 1, 'decisao']

    def get_topo(self):
        return self.topo
        
    def set_topo(self, valor):
        self.topo = valor
        
    def get_baixa(self):
        return self.baixa
        
    def set_baixa(self, valor):
        self.baixa = valor
        

    def analisar_decisao_RSI(self, rsi_valor):
        if rsi_valor == 0:
            return "Manter"
        elif rsi_valor > self.topo:
            return "Vender"  
        elif rsi_valor < self.baixa:
            return "Comprar"
        else:
            return "Manter"
        

    def calcular_diferenca(self):
        index_nova_linha = len(self.df) - 1
        close_atual = self.df['close'].iloc[index_nova_linha]
        if index_nova_linha < 1:
            self.df.loc[index_nova_linha, 'diferenca'] = close_atual
            return
        close_anterior = self.df['close'].iloc[index_nova_linha - 1]
        self.df.loc[index_nova_linha, 'diferenca'] = close_atual - close_anterior
        return self.df

    def calcular_ganho_perda(self):
        index_nova_linha = len(self.df) - 1
        self.df.loc[index_nova_linha, 'ganho'] = 0
        self.df.loc[index_nova_linha, 'perda'] = 0
        
        diferenca = self.df.at[index_nova_linha, 'diferenca']
        
        if diferenca > 0:
            self.df.loc[index_nova_linha, 'ganho'] = diferenca
        else:
            self.df.loc[index_nova_linha, 'perda'] = abs(diferenca)

        return self.df

    def calcular_media_ganho_perda(self, periodo):
        index_nova_linha = len(self.df) - 1

        if len(self.df) < periodo:
            # Calcula as médias simples das primeiras linhas
            media_ganho = self.df['ganho'].mean()
            media_perda = self.df['perda'].mean()
            self.df.at[index_nova_linha, 'media_ganho'] = media_ganho
            self.df.at[index_nova_linha, 'media_perda'] = media_perda
        else:
            media_ganho_anterior = self.df.at[index_nova_linha - 1, 'media_ganho']
            media_perda_anterior = self.df.at[index_nova_linha - 1, 'media_perda']

            # Atualiza as médias móveis com a última linha adicionada
            media_ganho_nova = ((media_ganho_anterior * (periodo - 1)) + self.df.at[index_nova_linha, 'ganho']) / periodo
            media_perda_nova = ((media_perda_anterior * (periodo - 1)) + self.df.at[index_nova_linha, 'perda']) / periodo

            self.df.at[index_nova_linha, 'media_ganho'] = media_ganho_nova
            self.df.at[index_nova_linha, 'media_perda'] = media_perda_nova

        return self.df

    def calcular_rsi(self):
        index_nova_linha = len(self.df) - 1

        media_ganho = self.df.at[index_nova_linha, 'media_ganho']
        media_perda = self.df.at[index_nova_linha, 'media_perda']

        if media_perda == 0:
            rs = 0
        else:
            rs = media_ganho / media_perda

        rsi = 100 - (100 / (1 + rs))
        self.df.at[index_nova_linha, 'rsi'] = rsi
        return self.df
    
    def atualizar_niveis_rsi(self, tamanho_janela=20, intervalo_recalculo=10):
        if len(self.df) >= tamanho_janela and len(self.df) % intervalo_recalculo == 0:
            valores_rsi = self.df['rsi'][-tamanho_janela:]
            valores_rsi_ordenados = np.sort(valores_rsi)
            maiores = valores_rsi_ordenados[-tamanho_janela//2:]
            menores = valores_rsi_ordenados[:tamanho_janela//2]
            topo = np.mean(maiores)
            baixa = np.mean(menores)
            self.set_topo(np.floor(topo))
            self.set_baixa(np.floor(baixa))

    
    def tomar_decisao_RSI(self):
        index_nova_linha = len(self.df) - 1
        rsi_valor = self.df.at[index_nova_linha, 'rsi']
        self.df.at[index_nova_linha, 'decisao'] = self.analisar_decisao_RSI(rsi_valor)
        self.df.at[index_nova_linha, 'topo'] = self.topo
        self.df.at[index_nova_linha, 'baixa'] = self.baixa
        #self.atualizar_niveis_rsi(20, 10)
        
    def plotar_grafico(self):
        self.df['rsi'] = self.df['rsi'].astype(float)
        
        plt.figure(figsize=(10, 5))
        
        plt.plot(self.df['date'], self.df['rsi'], label='RSI', color='blue')
        
        plt.plot(self.df['date'], self.df['topo'], label='Topo', color='red', linestyle='--')
        plt.plot(self.df['date'], self.df['baixa'], label='Baixa', color='green', linestyle='--')
        
        plt.title('Gráfico de RSI')
        plt.xlabel('Data')
        plt.ylabel('RSI')
        
        espacamento = math.ceil(len(self.df['date']) / 10)
        plt.xticks(self.df['date'][::espacamento], rotation=20)
        
        plt.legend()
        plt.show()
            

