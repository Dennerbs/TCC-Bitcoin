from abc import ABC, abstractmethod
import pandas as pd

class Indicador(ABC):
    def __init__(self, porcentagem_valor_total, valor_total, stop_loss, nome_indicador):
        self.df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
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
        self.porcentagem_valor_total = porcentagem_valor_total
        self.nome_indicador = nome_indicador
        self.valor_total = valor_total

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
        valor_ultima_compra = self.get_valor_ultima_compra()
        diferenca = valor_venda - valor_ultima_compra
        if valor_venda > valor_ultima_compra:
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
    
    def get_valor_ultima_compra(self):
        return self.valor_ultima_compra

    def set_linha_df(self, linha):
        self.df = self.df._append(linha, ignore_index=True) 
        
    def set_estado(self, valor):
        self.comprado = valor
    
    def get_estado(self):
        return self.comprado
    
    def set_porcentagem_valor_total(self, nova_porcentagem):
        self.porcentagem_valor_total = nova_porcentagem
        self.set_valor_disponivel(self.valor_total * (self.porcentagem_valor_total/100))
    
    def get_porcentagem_valor_total(self):
        return self.porcentagem_valor_total
    
    def get_stop_loss(self):
        return self.stop

    @abstractmethod
    def calcular_sinal(self, linha):
        pass
    
    @abstractmethod
    def plotar_grafico(self):
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