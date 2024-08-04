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
            parar_perda = indicador.get_stop(linha['close'])
            ultima_linha = (indice == (len(df) - 1))
            vender_bitcoin = sinal == 'Vender' or parar_perda or ultima_linha
            if vender_bitcoin and indicador.get_estado():
                valor_venda = indicador.get_quantidade_bitcoin() * linha['close']
                taxa_transacao = valor_venda * 0.001
                lucro_potencial = valor_venda - taxa_transacao
                valor_ultima_compra = indicador.get_valor_ultima_compra()
                lucro_minimo = valor_ultima_compra * indicador.get_lucro_minimo_venda()

                if (parar_perda or ultima_linha) or (sinal == 'Vender' and lucro_potencial > lucro_minimo):
                    indicador.set_estado(False)
                    indicador.set_valor_disponivel(lucro_potencial)
                    indicador.set_quantidade_vendas(lucro_potencial)
                    indicador.set_somatorio_taxas(taxa_transacao)
                    indicador.set_quantidade_bitcoin(0)
                    sinais_venda[indicador.nome_indicador]['x'].append(linha['date'])
                    sinais_venda[indicador.nome_indicador]['y'].append(linha['close'])
            elif sinal == 'Comprar':
                if not indicador.get_estado():
                    indicador.set_quantidade_compras()
                    indicador.set_estado(True)
                    valor_disponivel = indicador.get_valor_disponivel()
                    taxa_transacao = valor_disponivel * 0.001
                    valor_final = valor_disponivel - taxa_transacao
                    btc_a_comprar =  valor_final / linha['close']
                    indicador.set_quantidade_bitcoin(btc_a_comprar)
                    indicador.set_valor_disponivel(0)
                    indicador.set_somatorio_taxas(taxa_transacao)
                    sinais_compra[indicador.nome_indicador]['x'].append(linha['date'])
                    sinais_compra[indicador.nome_indicador]['y'].append(linha['close'])
            
            saldo+= indicador.get_valor_disponivel() + indicador.get_quantidade_bitcoin() * linha['close']
        valores['x'].append(linha['date'])
        valores['y'].append(saldo)

    saldo_total = 0
    taxas_total = 0
    ganhos_total = 0
    perdas_total = 0
    for indicador in indicadores:
        saldo_indicador = indicador.get_valor_disponivel()
        taxas_indicador = indicador.get_somatorio_taxas_transacao()
        ganhos_indicador = indicador.get_somatorio_ganhos()
        perdas_indicador = indicador.get_somatorio_perdas()
        
        print(f"###### Indicador: {indicador.nome_indicador} ######")
        print(f"Saldo indicador: {saldo_indicador}")
        print(f"Lucro: {indicador.calcular_lucro()}")
        print(f"Ganhos por operação (média): {indicador.calcular_lucro_por_operacao()}")
        print(f"Ganhos por dia: {indicador.calcular_lucro_diario(num_dias)}")
        print(f"Somatorio ganhos: {ganhos_indicador}")
        print(f"Somatorio perdas: {perdas_indicador}")
        print(f"Ganhos por operacao: {indicador.calcular_ganho_por_venda()}")
        print(f"Perdas por operacao: {indicador.calcular_perda_por_venda()}")    
        print(f"Somatorio Taxas de operacao: {taxas_indicador}")
        print(f"Taxas por operacao: {indicador.calcular_taxa_por_operacao()}")
        saldo_total += saldo_indicador    
        taxas_total += taxas_indicador    
        ganhos_total += ganhos_indicador    
        perdas_total += perdas_indicador    
        indicador.plotar_grafico()    


    print(f"###### Geral ######")
    print(f"Total ganhos: {ganhos_total}")
    print(f"Total perdas: {perdas_total}")
    print(f"Total taxas: {taxas_total}")
    print(f"Saldo Final: {saldo_total}")
    return saldo, sinais_compra, sinais_venda, valores
