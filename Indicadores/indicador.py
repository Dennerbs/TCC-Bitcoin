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
        self.qtd_compras = 0
        self.qtd_vendas = 0
        self.somatorio_ganhos = 0
        self.somatorio_perdas = 0

    def setValorDisponivel(self, valor):
        if self.valor_disponivel != 0 : 
            self.valor_ultima_compra = self.valor_disponivel 
        self.valor_disponivel = valor
        
    def setQtdCompras(self):
        self.qtd_compras += 1
    
    def getQtdCompras(self):
        return self.qtd_compras
    
    def setQtdVendas(self, valor_venda):
        self.qtd_vendas += 1
        diferenca = valor_venda - self.valor_ultima_compra
        if valor_venda > self.valor_ultima_compra:
            self.somatorio_ganhos += diferenca
        else:
            self.somatorio_perdas +=diferenca
    
    def getQtdVendas(self):
        return self.qtd_vendas
    
    def getValorDisponivel(self):
        return self.valor_disponivel
    
    def setValorizacao(self, valor):
        self.valorizacao = valor
    
    def getValorizacao(self, valor_atual_bitcoin):
        valorizacao_momento = self.quantidade_bitcoin * valor_atual_bitcoin
        diferenca_momento = ((valorizacao_momento - self.valor_ultima_compra) / valorizacao_momento) * 100 if valorizacao_momento > 0 else 0
        return diferenca_momento
    
    def getStop(self, valor_atual_bitcoin):
        return self.getValorizacao(valor_atual_bitcoin) <= self.stop
        
    def setQuantidadeBitcoin(self, valor):
        self.quantidade_bitcoin = valor
    
    def getQuantidadeBitcoin(self):
        return self.quantidade_bitcoin

    def setLinhaDf(self, linha):
        self.df = self.df._append(linha, ignore_index=True)  # Adicione a nova linha ao DataFrame
        
    def setEstado(self, valor):
        self.comprado = valor
    
    def getEstado(self):
        return self.comprado

    @abstractmethod
    def calcular_sinal(self, linha):
        pass
    
    def calcular_somatorio_ganhos_perdas(self):
        return self.somatorio_ganhos + self.somatorio_perdas

    def calcular_magnitude_ganhos_por_operacao_media(self):
        total_operacoes = self.qtd_compras + self.qtd_vendas
        if total_operacoes == 0:
            return 0
        return (self.somatorio_ganhos + self.somatorio_perdas) / total_operacoes

    def calcular_magnitude_ganhos_por_dia(self, num_dias):
        if num_dias == 0:
            return 0
        return (self.somatorio_ganhos + self.somatorio_perdas) / num_dias

    def calcular_magnitude_ganho_operacoes_com_ganho(self):
        if self.qtd_vendas == 0:
            return 0
        return self.somatorio_ganhos / self.qtd_vendas

    def calcular_magnitude_ganho_operacoes_com_perda(self):
        if self.qtd_vendas == 0:
            return 0
        return self.somatorio_perdas / self.qtd_vendas