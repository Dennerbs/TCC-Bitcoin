from abc import ABC, abstractmethod
import pandas as pd

class Indicador(ABC):
    def __init__(self, porcentagem_lucro_minimo_venda, porcentagem_valor_total, valor_total, stop_loss, nome_indicador):
        self.df = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume'])
        self.comprado = False
        self.quantidade_bitcoin = 0
        self.porcentagem_lucro_minimo_venda = porcentagem_lucro_minimo_venda
        self.valorizacao = 0
        self.valor_ultima_compra = 0
        self.valor_disponivel = valor_total * (porcentagem_valor_total/100)
        self.stop = stop_loss
        self.quantidade_compras = 0
        self.quantidade_vendas = 0
        self.somatorio_ganhos = 0
        self.somatorio_perdas = 0
        self.somatorio_taxas = 0
        self.porcentagem_valor_total = porcentagem_valor_total
        self.nome_indicador = nome_indicador
        self.valor_total = valor_total

    def set_valor_disponivel(self, valor):
        self.valor_disponivel = float(valor)
        
    def set_valor_ultima_compra(self, valor): 
        self.valor_ultima_compra = float(valor)
        
    def get_lucro_minimo_venda(self):
        return self.get_valor_ultima_compra() * self.get_porcentagem_lucro_minimo_venda()
    
    def get_porcentagem_lucro_minimo_venda(self):
        return self.porcentagem_lucro_minimo_venda
    
    def get_valor_disponivel(self):
        return self.valor_disponivel
        
    def set_quantidade_compras(self):
        self.quantidade_compras += 1
        
    def get_somatorio_taxas_transacao(self):
        return self.somatorio_taxas
    
    def get_total_operacao(self):
        return self.quantidade_compras + self.quantidade_vendas
        
    def set_somatorio_taxas(self, taxa):
        self.somatorio_taxas += float(taxa)
    
    def get_quantidade_compras(self):
        return self.quantidade_compras
    
    def set_quantidade_vendas(self, valor_venda):
        self.quantidade_vendas += 1
        self.calcular_resultado_venda(float(valor_venda))
    
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
        self.valorizacao = float(valor)
    
    def get_valorizacao(self, valor_atual_bitcoin):
        valorizacao_momento = self.quantidade_bitcoin * valor_atual_bitcoin
        diferenca_momento = ((valorizacao_momento - self.valor_ultima_compra) / valorizacao_momento) * 100 if valorizacao_momento > 0 else 0
        return diferenca_momento
    
    def get_stop(self, valor_atual_bitcoin):
        if not self.comprado:
            return False
        return self.get_valorizacao(valor_atual_bitcoin) <= self.stop
        
    def set_quantidade_bitcoin(self, valor):
        self.quantidade_bitcoin = float(valor)
    
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
    
    def get_somatorio_ganhos(self):
        return self.somatorio_ganhos
    
    def get_somatorio_perdas(self):
        return self.somatorio_perdas

    @abstractmethod
    def calcular_sinal(self, linha):
        pass
    
    @abstractmethod
    def plotar_grafico(self):
        pass
    
    @abstractmethod
    def get_conteudo_grafico(self):
        pass
    
    def calcular_lucro(self):
        return self.somatorio_ganhos + self.somatorio_perdas

    def calcular_lucro_por_operacao(self):
        total_operacoes = self.get_total_operacao()
        if total_operacoes == 0:
            return 0
        return (self.somatorio_ganhos + self.somatorio_perdas) / total_operacoes
    
    def calcular_taxa_por_operacao(self):
        total_operacoes = self.get_total_operacao()
        if total_operacoes == 0:
            return 0
        return self.get_somatorio_taxas_transacao() / total_operacoes

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