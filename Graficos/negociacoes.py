import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.dates import DateFormatter
from pandas.plotting import register_matplotlib_converters
import math

def plot_negociacoes(datas, fechamento, sinais_compra, sinais_venda):
    
    plt.figure(figsize=(16, 12))
    plt.plot(datas, fechamento, label="Preço do Bitcoin")
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
        )
    for index, sinal in enumerate(sinais_venda):
        plt.scatter(
        sinais_venda[sinal]['x'],
        sinais_venda[sinal]['y'],
        color=cores_venda[index],
        marker="v",
        label=f"Venda - {sinal}",
        )

    # plt.scatter(
    #     sinais_compra['MACD']['x'],
    #     sinais_compra['MACD']['y'],
    #     color="green",
    #     marker="^",
    #     label="Compra - MACD",
    # )
    # plt.scatter(
    #     sinais_compra['RSI']['x'],
    #     sinais_compra['RSI']['y'],
    #     color="blue",
    #     marker="^",
    #     label="Compra - RSI",
    # )
    # plt.scatter(
    #     sinais_venda['MACD']['x'],
    #     sinais_venda['MACD']['y'],
    #     color="red",
    #     marker="v",
    #     label="Venda - MACD",
    # )
    # plt.scatter(
    #     sinais_venda['RSI']['x'],
    #     sinais_venda['RSI']['y'],
    #     color="orange",
    #     marker="v",
    #     label="Venda - RSI",
    # )

    plt.xlabel("Data")
    plt.ylabel("Preço do Bitcoin")
    plt.title("Compras e Vendas")
    plt.legend()
    plt.show()
    
def graficoEvolucaoDinheiro(valores):
    plt.figure(figsize=(16, 12))
    plt.plot(
        valores["x"],
        valores["y"],
        label="Evolução do Dinheiro",
        linestyle="-",
        #marker="o",
        color="blue",
    )
    
 
    date_format = DateFormatter("%Y-%m-%d")
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gcf().autofmt_xdate()

    plt.xlabel("Datas")
    plt.ylabel("Valor em USD")
    plt.title("Evolução do Dinheiro durante Compras e Vendas")
    plt.legend()
    plt.show()
    
def graficoEvolucaoDinheiro(valores, valorBuyAndHold = 0, minutos = False, sinais_compra = {}, df = []):

    plt.figure(figsize=(12, 8))
    plt.plot(
        valores["x"],
        valores["y"],
        label="Evolução do Dinheiro",
        linestyle="-",
        color="blue",
    )
    if minutos :
        espacamento = math.ceil(len(valores['x']) / 10)
        plt.xticks(valores["x"][::espacamento], rotation=20)
    
    if valorBuyAndHold:
        data_mais_antiga = min(min(sinais_compra[sinal]["x"]) for sinal in sinais_compra)
        
        # Encontrando o índice da data mais antiga nos valores['x']
        indice_data_mais_antiga = df.index[df['date'] == data_mais_antiga][0]    
        primeira_compra = valorBuyAndHold / sinais_compra[min(sinais_compra, key=lambda x: min(sinais_compra[x]["x"]))]["y"][0]
        dfBH = df.loc[indice_data_mais_antiga:]
        buy_and_hold_y = [primeira_compra * y for y in dfBH['close']]
        
        plt.plot(
            dfBH['date'],
            buy_and_hold_y,
            label="Buy and Hold",
            linestyle="--",
            color="black",
        )
        
        

    # date_format = DateFormatter("%Y-%m-%d")
    # plt.gca().xaxis.set_major_formatter(date_format)
    # plt.gcf().autofmt_xdate()

    plt.xlabel("Datas")
    plt.ylabel("Valor em USD")
    plt.title("Evolução do Patrimonio durante Compras e Vendas")
    plt.legend()
    plt.show()


