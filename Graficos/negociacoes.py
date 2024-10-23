import matplotlib.pyplot as plt
import pandas as pd
import math

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
    
    
def plotar_evolucao_dinheiro(valores, valor_buyAndHold=0, minutos=False, sinais_compra={}, df=[]):
    plt.figure(figsize=(12, 8))
    plt.plot(
        valores["x"],
        valores["y"],
        label="Evolução do Dinheiro",
        linestyle="-",
        color="blue",
    )
    if minutos:
        espacamento = math.ceil(len(valores['x']) / 10)
        plt.xticks(valores["x"][::espacamento], rotation=20)

    if valor_buyAndHold:
        # Filtrar sinais de compra que têm dados
        sinais_validos = {k: v for k, v in sinais_compra.items() if len(v["x"]) > 0}
        
        if sinais_validos:
            # Encontrar a menor data de compra
            data_primeira_compra = min(min(sinal["x"]) for sinal in sinais_validos.values())

            indice_data_primeira_compra = (pd.to_datetime(df['date']) - pd.to_datetime(data_primeira_compra)).abs().idxmin()

            # Encontrar o indicador com a menor data de compra
            indicador_primeira_compra = min(sinais_validos, key=lambda x: min(sinais_validos[x]["x"]))
            valor_bitcoin_data_primeira_compra = sinais_validos[indicador_primeira_compra]["y"][0]

            quantidade_inicial_bitcoin = valor_buyAndHold / valor_bitcoin_data_primeira_compra

            dfBH = df.loc[indice_data_primeira_compra:]

            buy_and_hold_valores = quantidade_inicial_bitcoin * dfBH['close']
        
            plt.plot(
                dfBH['date'],
                buy_and_hold_valores,
                label="Buy and Hold",
                linestyle="--",
                color="black",
            )
        else:
            print("Nenhum sinal de compra válido encontrado.")

    plt.xlabel("Datas")
    plt.ylabel("Valor em Real")
    plt.title("Evolução do Patrimonio durante Compras e Vendas")
    plt.legend()
    plt.show()


