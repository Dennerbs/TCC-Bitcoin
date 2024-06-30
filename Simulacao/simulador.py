def simulador(df, indicadores, num_dias):
    sinais_compra = {indicador.nome_indicador: {'x':[], 'y':[]} for indicador in indicadores}
    sinais_venda = {indicador.nome_indicador: {'x':[], 'y':[]} for indicador in indicadores}
    valores = {'x':[], 'y':[]}

    for indice, linha in df.iterrows():
        saldo = 0
        print("indice: ", indice)
        for i, indicador in enumerate(indicadores):
            sinal = indicador.calcular_sinal(linha)
            #se sinal vender ou for ultima linha do df
            if sinal == 'Vender' or indicador.get_stop(linha['close']) or (indice == (len(df) - 1)):
                if indicador.get_estado():
                    indicador.set_estado(False)
                    valor_venda= indicador.get_quantidade_bitcoin() * linha['close']
                    indicador.set_valor_disponivel(valor_venda)
                    indicador.set_quantidade_vendas(valor_venda)
                    indicador.set_quantidade_bitcoin(0)
                    sinais_venda[indicador.nome_indicador]['x'].append(linha['date'])
                    sinais_venda[indicador.nome_indicador]['y'].append(linha['close'])
            elif sinal == 'Comprar':
                if not indicador.get_estado():
                    indicador.set_quantidade_compras()
                    indicador.set_estado(True)
                    btc_a_comprar = indicador.get_valor_disponivel() / linha['close']
                    indicador.set_quantidade_bitcoin(btc_a_comprar)
                    indicador.set_valor_disponivel(0)
                    sinais_compra[indicador.nome_indicador]['x'].append(linha['date'])
                    sinais_compra[indicador.nome_indicador]['y'].append(linha['close'])
            
            saldo+= indicador.get_valor_disponivel() + indicador.get_quantidade_bitcoin() * linha['close']
        valores['x'].append(linha['date'])
        valores['y'].append(saldo)

    for indicador in indicadores:
        print(f"Indicador: {indicador.nome_indicador}")
        print(f"Lucro: {indicador.calcular_lucro()}")
        print(f"Ganhos por operação (média): {indicador.calcular_lucro_por_operacao()}")
        print(f"Ganhos por dia: {indicador.calcular_lucro_diario(num_dias)}")
        print(f"Soma de ganhos: {indicador.calcular_ganho_por_venda()}")
        print(f"Soma de perdas: {indicador.calcular_perda_por_venda()}")    
        print(f"Saldo Final: {saldo}")
        indicador.plotar_grafico()    


    return saldo, sinais_compra, sinais_venda, valores
