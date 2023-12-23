import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from matplotlib.dates import DateFormatter


def calcular_diferenca_momento(
    maior_valor_momento, valorizacao_momento, porcentagem_stop
):
    diferenca_momento = (
        ((maior_valor_momento - valorizacao_momento) / maior_valor_momento) * 100
        if maior_valor_momento > 0
        else 0
    )
    return diferenca_momento > porcentagem_stop


def realizar_venda(
    valor_total,
    total_bitcoin,
    valor_bitcoin,
    soma_valores_vendas,
    soma_valores_compras,
    valores,
    pontos_venda,
    data,
):
    vendido = total_bitcoin * valor_bitcoin
    valor_total = vendido
    soma_valores_vendas += vendido
    diferenca = soma_valores_vendas - soma_valores_compras
    print(
        f"Data: {data} | bitcoins vendidos: {total_bitcoin} | Bitcoin USD: {valor_bitcoin} | Valor da venda: {vendido} | Ganho Total: {diferenca}"
    )
    total_bitcoin = 0

    valores["x"].append(data)
    valores["y"].append(vendido)
    valores["Ybh"].append((valores["primeira_compra"] * valor_bitcoin))
    pontos_venda["x"].append(data)
    pontos_venda["y"].append(valor_bitcoin)
    return (
        valor_total,
        soma_valores_vendas,
        diferenca,
        total_bitcoin,
        valores,
        pontos_venda,
    )


def somar_negociacao(
    diferenca, operacoes_ganho, soma_ganhos, operacoes_perda, soma_perdas, ganho_total
):
    if diferenca > 0:
        operacoes_ganho += 1
        soma_ganhos += diferenca
    else:
        operacoes_perda += 1
        soma_perdas += diferenca
    ganho_total += diferenca

    return operacoes_ganho, soma_ganhos, operacoes_perda, soma_perdas, ganho_total


def realizar_compra(
    valor_total,
    valor_bitcoin,
    total_bitcoin,
    soma_valores_compras,
    maior_valor_momento,
    valores,
    pontos_compra,
    data,
):
    quantidade_comprada = valor_total / valor_bitcoin
    total_bitcoin = quantidade_comprada
    soma_valores_compras += valor_total
    maior_valor_momento = valor_total
    print(
        f"Data: {data}| Valor de compra: {soma_valores_compras} | Bitcoin USD: {valor_bitcoin} | Quantidade comprada: {quantidade_comprada}| Total comprado : {soma_valores_compras}"
    )
    valores["x"].append(data)
    valores["y"].append(valor_total)
    
    pontos_compra["x"].append(data)
    pontos_compra["y"].append(valor_bitcoin)
    valor_total = 0
    return valor_total, total_bitcoin, soma_valores_compras, maior_valor_momento


def simulador(df, valorTotal, porc_stop, numero_dias):
    compras = vendas = total_bitcoin = soma_valores_compras = soma_valores_vendas = 0
    operacoes_ganho = operacoes_perda = soma_ganhos = soma_perdas = ganho_total = 0
    comprado = False
    primeira_compra = False

    valores = {"x": [], "y": [], "Ybh":[]}
    pontos_compra = {"x": [], "y": []}
    pontos_venda = {"x": [], "y": []}

    maior_valor_momento = 0

    for i, row in df.iterrows():
        acao = row["decisao"]
        valor_bitcoin = row["close"]

        if i == len(df) - 1 and comprado:
            vendas += 1
            (
                valorTotal,
                soma_valores_vendas,
                diferenca,
                total_bitcoin,
                valores,
                pontos_venda,
            ) = realizar_venda(
                valorTotal,
                total_bitcoin,
                valor_bitcoin,
                soma_valores_vendas,
                soma_valores_compras,
                valores,
                pontos_venda,
                row["date"],
            )
            break

        if acao == "Comprar" and not comprado and not i == len(df) - 1:
            comprado = True
            compras += 1
            if not primeira_compra:
                valores["primeira_compra"] = valorTotal / valor_bitcoin
                primeira_compra = True

            (
                valorTotal,
                total_bitcoin,
                soma_valores_compras,
                maior_valor_momento,
            ) = realizar_compra(
                valorTotal,
                valor_bitcoin,
                total_bitcoin,
                soma_valores_compras,
                maior_valor_momento,
                valores,
                pontos_compra,
                row["date"],
            )
           
               

        elif acao == "Vender" and comprado:
            comprado = False
            vendas += 1
            (
                valorTotal,
                soma_valores_vendas,
                diferenca,
                total_bitcoin,
                valores,
                pontos_venda,
            ) = realizar_venda(
                valorTotal,
                total_bitcoin,
                valor_bitcoin,
                soma_valores_vendas,
                soma_valores_compras,
                valores,
                pontos_venda,
                row["date"],
            )

            (
                operacoes_ganho,
                soma_ganhos,
                operacoes_perda,
                soma_perdas,
                ganho_total,
            ) = somar_negociacao(
                diferenca,
                operacoes_ganho,
                soma_ganhos,
                operacoes_perda,
                soma_perdas,
                ganho_total,
            )

        elif comprado:
            valorizacao_momento = total_bitcoin * valor_bitcoin
            diferenca_momento = calcular_diferenca_momento(
                maior_valor_momento, valorizacao_momento, porc_stop
            )
            print(
                f"{maior_valor_momento} == {valorizacao_momento}---------{diferenca_momento} > {porc_stop}-----------------------"
            )

            if valorizacao_momento > maior_valor_momento:
                maior_valor_momento = valorizacao_momento
            elif diferenca_momento:
                comprado = False
                vendas += 1
                (
                    valorTotal,
                    soma_valores_vendas,
                    diferenca,
                    total_bitcoin,
                    valores,
                    pontos_venda,
                ) = realizar_venda(
                    valorTotal,
                    total_bitcoin,
                    valor_bitcoin,
                    soma_valores_vendas,
                    soma_valores_compras,
                    valores,
                    pontos_venda,
                    row["date"],
                )

                (
                    operacoes_ganho,
                    soma_ganhos,
                    operacoes_perda,
                    soma_perdas,
                    ganho_total,
                ) = somar_negociacao(
                    diferenca,
                    operacoes_ganho,
                    soma_ganhos,
                    operacoes_perda,
                    soma_perdas,
                    ganho_total,
                )

    magnitude_ganhos_operacao = (
        soma_ganhos / operacoes_ganho if operacoes_ganho > 0 else 0
    )
    magnitude_perdas_operacao = (
        soma_perdas / operacoes_perda if operacoes_perda > 0 else 0
    )
    magnitude_ganhos_dia = ganho_total / numero_dias

    print(f"Número de compras: {compras}")
    print(f"Número de vendas: {vendas}")
    print(f"Ganho total: {soma_ganhos:.2f} USD")
    print(f"Perda total: {soma_perdas:.2f} USD")
    print(f"Lucro: {soma_valores_vendas - soma_valores_compras:.2f} USD")
    print(
        f"Magnitude de Ganhos por Operação (Média): {magnitude_ganhos_operacao:.2f} USD por operação"
    )
    print(f"Magnitude de Ganhos por Dia: {magnitude_ganhos_dia:.2f} USD por dia")
    print(
        f"Magnitude de Ganho das Operações com Ganho: {magnitude_ganhos_operacao:.2f} USD por operação"
    )
    print(
        f"Magnitude de Ganho das Operações com Perda: {magnitude_perdas_operacao:.2f} USD por operação"
    )

    valores["Xbh"] = pontos_venda["x"].copy()
    graficoEvolucaoDinheiro(valores)

    graficoVendas(df["date"], df["close"], pontos_compra, pontos_venda)


def graficoEvolucaoDinheiro(valores):
    plt.figure(figsize=(16, 12))
    valores["Ybh"][0] = valores["y"][0]
    valores["Xbh"][0] = valores["x"][0]
    plt.plot(
        valores["x"],
        valores["y"],
        label="Evolução do Dinheiro",
        linestyle="-",
        marker="o",
        color="blue",
    )
    plt.plot(
        valores["Xbh"],
        valores["Ybh"],
        label="Evolução Buy and Hold",
        linestyle="-",
        #marker="-",
        color="black",
    )
 
    date_format = DateFormatter("%Y-%m-%d")
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gcf().autofmt_xdate()

    plt.xlabel("Datas")
    plt.ylabel("Valor em USD")
    plt.title("Evolução do Dinheiro durante Compras e Vendas")
    plt.legend()
    plt.show()


def graficoVendas(datas, fechamento, pontos_compra, pontos_venda):
    plt.figure(figsize=(16, 12))
    plt.plot(datas, fechamento, label="Preço do Bitcoin")
    print(pontos_venda["x"][0])
    plt.scatter(
        pontos_compra["x"],
        pontos_compra["y"],
        color="green",
        marker="^",
        label="Compra",
    )
    plt.scatter(
        pontos_venda["x"], pontos_venda["y"], color="red", marker="v", label="Venda"
    )

    date_format = DateFormatter("%Y-%m-%d")
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gcf().autofmt_xdate()

    plt.xlabel("Índice")
    plt.ylabel("Preço do Bitcoin")
    plt.title("Compras e Vendas")
    plt.legend()
    plt.show()
