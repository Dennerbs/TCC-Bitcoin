import matplotlib.pyplot as plt
import pandas as pd
import math
from Utils.utils import calcular_drawdown

def plotar_negociacoes(datas, fechamento, sinais_compra, sinais_venda):
    
    plt.figure(figsize=(16, 12))
    plt.plot(datas, fechamento, label="Preço do Bitcoin",zorder=1)
    espacamento = math.ceil(len(datas) / 10)
    plt.xticks(datas[::espacamento], rotation=20)
    cores_compra = ['green', 'blue', 'purple']
    cores_venda = ['red', 'orange', 'yellow']
    
    for index, sinal in enumerate(sinais_compra):
        plt.scatter(
        sinais_compra[sinal]['x'],
        sinais_compra[sinal]['y'],
        color=cores_compra[index],
        marker="^",
        label=f"Compra - {sinal}",
        zorder=2
        )
    for index, sinal in enumerate(sinais_venda):
        plt.scatter(
        sinais_venda[sinal]['x'],
        sinais_venda[sinal]['y'],
        color=cores_venda[index],
        marker="v",
        label=f"Venda - {sinal}",
        zorder=2
        )

    plt.xlabel("Data")
    plt.ylabel("Preço do Bitcoin")
    plt.title("Compras e Vendas")
    plt.legend()
    plt.show()
    


def plotar_drawdown(valores_investimento, valores_bh):
    datas_bh, evolucao_bh = valores_bh
    drawndown_investimento = calcular_drawdown(valores_investimento["y"])
    drawndown_bh = calcular_drawdown(evolucao_bh)

    print(f'Maior drawndown valor investido: {min(drawndown_investimento)}')
    print(f'Maior drawndown buy and hold: {min(drawndown_bh)}')
    
    plt.figure(figsize=(12, 8))
    plt.subplot(2, 1, 1)
    plt.fill_between(valores_investimento["x"], drawndown_investimento, color='red', alpha=0.5)
    plt.title('Drawdown Investimento')
    plt.xlabel('Data')
    plt.ylabel('Drawdown (%)')
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    espacamento = math.ceil(len(valores_investimento["x"]) / 10)
    plt.xticks(valores_investimento["x"][::espacamento], rotation=20)
    plt.grid()
    
    plt.subplot(2, 1, 2)
    plt.fill_between(datas_bh, drawndown_bh, color='red', alpha=0.5)
    plt.title('Drawdown buy and hold')
    plt.xlabel('Data')
    plt.ylabel('Drawdown (%)')
    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    espacamento = math.ceil(len(datas_bh) / 10)
    plt.xticks(datas_bh[::espacamento], rotation=20)
    plt.grid()
    
    plt.tight_layout()
    plt.show()

def plotar_evolucao_dinheiro(valores_indicadores, valores_buyAndHold):
    plt.figure(figsize=(12, 8))
    plt.plot(
        valores_indicadores["x"],
        valores_indicadores["y"],
        label="Evolução do Dinheiro",
        linestyle="-",
        color="blue",
    )

    espacamento = math.ceil(len(valores_indicadores['x']) / 10)
    plt.xticks(valores_indicadores["x"][::espacamento], rotation=20)
    
    if valores_buyAndHold:
        data_bh, buy_and_hold_valores = valores_buyAndHold
        
        plt.plot(
            data_bh,
            buy_and_hold_valores,
            label="Buy and Hold",
            linestyle="--",
            color="black",
        )
            
    
    plt.xlabel("Datas")
    plt.ylabel("Valor em Dólar (US$)")
    plt.title("Evolução do Patrimônio durante Compras e Vendas")
    plt.legend()
    plt.show()


