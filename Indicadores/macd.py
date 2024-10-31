from .indicador import Indicador
import pandas as pd
import matplotlib.pyplot as plt
import math
from matplotlib.dates import DateFormatter

class MACD(Indicador):
    def __init__(self, periodo_curto, periodo_longo, valor_total, porcentagem_lucro_minimo_venda, porcentagem_valor_total, stop_loss, periodo_linha_sinal=9):
        super().__init__(porcentagem_lucro_minimo_venda, porcentagem_valor_total, valor_total, stop_loss, self.__class__.__name__)
        self.periodo_curto = periodo_curto
        self.periodo_longo = periodo_longo
        self.signal_window = periodo_linha_sinal
        self.linha_curta = []
        self.linha_longa = []
        self.linha_macd = []


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
            self.df.loc[index_nova_linha, 'MACD'] = 0
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
        

    def tomar_decisao_macd(self):
        decisao = 'Manter'
        index_nova_linha = len(self.df) - 1
        if index_nova_linha <= self.periodo_curto:
            self.df.loc[index_nova_linha, 'decisao'] = decisao
            return
        macd_atual = self.df['MACD'].iloc[index_nova_linha]
        linha_macd_atual = self.df['linha_macd'].iloc[index_nova_linha]
        

        if macd_atual > linha_macd_atual:
            decisao = 'Comprar'
        elif macd_atual < linha_macd_atual:
            decisao = 'Vender'

        self.df.loc[index_nova_linha, 'decisao'] = decisao
        
    def get_conteudo_grafico(self):
        return {
            "macd": self.df['MACD'].iloc[-1],
            "linha_macd": self.linha_macd[-1],
        }

    def plotar_grafico(self, dados_graficos):
        datas = dados_graficos['data']
        quantidade_datas = len(datas)
        macd = dados_graficos['macd'][:quantidade_datas]
        linha_macd = dados_graficos['linha_macd'][:quantidade_datas]
        
        plt.figure(figsize=(10, 6))
        plt.plot(datas, macd, label='MACD', color='blue')
        plt.plot(datas, linha_macd, label='Linha MACD', color='red')
        
        espacamento = math.ceil(len(datas) / 10)
        plt.xticks(datas[::espacamento], rotation=20)

        plt.title('MACD')
        plt.xlabel('Data')
        plt.legend()
        plt.show()
