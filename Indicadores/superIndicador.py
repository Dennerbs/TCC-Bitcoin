from collections import Counter
from .indicador import Indicador

class SuperIndicador(Indicador):
    def __init__(self, indicadores, valor_total):
        porcentagem_valor_total = 0 
        stop_loss = 0 
        soma_stop_loss = 0
        novo_nome_class = ''
        for indicador in indicadores:
            porcentagem_valor_total += indicador.get_porcentagem_valor_total()
            soma_stop_loss += indicador.get_stop_loss()
            novo_nome_class += f'{indicador.__class__.__name__}-'
        stop_loss = soma_stop_loss / len(indicadores)
        
        super().__init__(porcentagem_valor_total, valor_total, stop_loss, novo_nome_class[:-1])
        self.indicadores = indicadores
        
    
    def calcular_sinal(self, linha):
        sinais = [indicador.calcular_sinal(linha) for indicador in self.indicadores]
        contagem_sinais = Counter(sinais)
        
        sinais_compra = contagem_sinais.get("Comprar", 0)
        sinais_venda = contagem_sinais.get("Vender", 0)
        sinais_manter = contagem_sinais.get("Manter", 0)

        if sinais_compra > max(sinais_venda, sinais_manter):
            print(contagem_sinais)
            return "Comprar"
        elif sinais_venda > max(sinais_compra, sinais_manter):
            print(contagem_sinais)
            return "Vender"
        
        return "Manter"
    
    def plotar_grafico(self):
        for indicador in self.indicadores:
            indicador.plotar_grafico()
        