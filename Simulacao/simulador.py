def simulador(df, indicadores, num_dias):
    sinais_compra = {indicador.__class__.__name__: {'x':[], 'y':[]} for indicador in indicadores}
    sinais_venda = {indicador.__class__.__name__: {'x':[], 'y':[]} for indicador in indicadores}
    valores = {'x':[], 'y':[]}

    for indice, linha in df.iterrows():
        saldo = 0
        print("indice: ", indice)
        for i, indicador in enumerate(indicadores):
            sinal = indicador.calcular_sinal(linha)
            #se sinal vender ou for ultima linha do df
            if sinal == 'Vender' or indicador.getStop(linha['close']) or (indice == (len(df) - 1)):
                if indicador.getEstado():
                    indicador.setEstado(False)
                    valor_venda= indicador.getQuantidadeBitcoin() * linha['close']
                    indicador.setValorDisponivel(valor_venda)
                    indicador.setQtdVendas(valor_venda)
                    indicador.setQuantidadeBitcoin(0)
                    sinais_venda[indicador.__class__.__name__]['x'].append(linha['date'])
                    sinais_venda[indicador.__class__.__name__]['y'].append(linha['close'])
            elif sinal == 'Comprar':
                if not indicador.getEstado():
                    indicador.setQtdCompras()
                    indicador.setEstado(True)
                    btc_a_comprar = indicador.getValorDisponivel() / linha['close']
                    indicador.setQuantidadeBitcoin(btc_a_comprar)
                    indicador.setValorDisponivel(0)
                    sinais_compra[indicador.__class__.__name__]['x'].append(linha['date'])
                    sinais_compra[indicador.__class__.__name__]['y'].append(linha['close'])
            
            saldo+= indicador.getValorDisponivel() + indicador.getQuantidadeBitcoin() * linha['close']
        valores['x'].append(linha['date'])
        valores['y'].append(saldo)

    for indicador in indicadores:
        print(f"Indicador: {indicador.__class__.__name__}")
        print(f"Somatório de ganhos/perdas: {indicador.calcular_somatorio_ganhos_perdas()}")
        print(f"Magnitude de ganhos por operação (média): {indicador.calcular_magnitude_ganhos_por_operacao_media()}")
        print(f"Magnitude de ganhos por dia: {indicador.calcular_magnitude_ganhos_por_dia(num_dias)}")
        print(f"Magnitude de ganho das operações com ganho: {indicador.calcular_magnitude_ganho_operacoes_com_ganho()}")
        print(f"Magnitude de ganho das operações com perda: {indicador.calcular_magnitude_ganho_operacoes_com_perda()}")    


    return saldo, sinais_compra, sinais_venda, valores
