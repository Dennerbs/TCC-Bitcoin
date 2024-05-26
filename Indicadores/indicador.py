from abc import ABC, abstractmethod
import pandas as pd

class Indicador(ABC):
    def __init__(self, porcentagem_valor_total, valor_total, stop_loss):
        self.df = pd.DataFrame(columns=['unix','date','symbol','open','high','low','close','Volume BTC','Volume USD'])
        self.comprado = False
        self.quantidade_bitcoin = 0
        self.valorizacao = 0
        self.valor_ultima_compra = 0
        self.valor_disponivel = valor_total * (porcentagem_valor_total/100)
        self.stop = stop_loss
        self.quantidade_compras = 0
        self.quantidade_vendas = 0
        self.somatorio_ganhos = 0
        self.somatorio_perdas = 0

    def set_valor_disponivel(self, valor):
        if self.valor_disponivel != 0 : 
            self.valor_ultima_compra = self.valor_disponivel 
        self.valor_disponivel = valor
        
    def get_valor_disponivel(self):
        return self.valor_disponivel
        
    def set_quantidade_compras(self):
        self.quantidade_compras += 1
    
    def get_quantidade_compras(self):
        return self.quantidade_compras
    
    def set_quantidade_vendas(self, valor_venda):
        self.quantidade_vendas += 1
        self.calcular_resultado_venda(valor_venda)
    
    def get_quantidade_vendas(self):
        return self.quantidade_vendas
    
    def calcular_resultado_venda(self, valor_venda):
        diferenca = valor_venda - self.valor_ultima_compra
        if valor_venda > self.valor_ultima_compra:
            self.somatorio_ganhos += diferenca
        else:
            self.somatorio_perdas += diferenca
    
    
    def set_valorizacao(self, valor):
        self.valorizacao = valor
    
    def get_valorizacao(self, valor_atual_bitcoin):
        valorizacao_momento = self.quantidade_bitcoin * valor_atual_bitcoin
        diferenca_momento = ((valorizacao_momento - self.valor_ultima_compra) / valorizacao_momento) * 100 if valorizacao_momento > 0 else 0
        return diferenca_momento
    
    def get_stop(self, valor_atual_bitcoin):
        return self.get_valorizacao(valor_atual_bitcoin) <= self.stop
        
    def set_quantidade_bitcoin(self, valor):
        self.quantidade_bitcoin = valor
    
    def get_quantidade_bitcoin(self):
        return self.quantidade_bitcoin

    def set_linha_df(self, linha):
        self.df = self.df._append(linha, ignore_index=True)  # Adicione a nova linha ao DataFrame
        
    def set_estado(self, valor):
        self.comprado = valor
    
    def get_estado(self):
        return self.comprado

    @abstractmethod
    def calcular_sinal(self, linha):
        pass
    
    def calcular_lucro(self):
        return self.somatorio_ganhos + self.somatorio_perdas

    def calcular_lucro_por_operacao(self):
        total_operacoes = self.quantidade_compras + self.quantidade_vendas
        if total_operacoes == 0:
            return 0
        return (self.somatorio_ganhos + self.somatorio_perdas) / total_operacoes

    def calcular_lucro_diario(self, num_dias):
        if num_dias == 0:
            return 0
        return (self.somatorio_ganhos + self.somatorio_perdas) / num_dias

    def calcular_ganho_por_venda(self):
        if self.quantidade_vendas == 0:
            return 0
        return self.somatorio_ganhos / self.quantidade_vendas

    def calcular_perda_por_venda(self):
        if self.quantidade_vendas == 0:
            return 0
        return self.somatorio_perdas / self.quantidade_vendas