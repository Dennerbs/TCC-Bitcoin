from Utils.utils import formatar_log_compra_venda, formatar_log_indicador, autorizar_compra, autorizar_venda, get_ordem_venda_simulacao, get_ordem_compra_simulacao, tratar_ordem
import logging


# Configuração básica do logging
logging.basicConfig(filename='trade_logs_SIMULACAO.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def simulador(df, indicadores, indicadores_preparados, valor_total, ambiente='PRINCIPAL'):
    log_inicial = {
        "valor_inicial": valor_total,
        "config_indicadores": indicadores_preparados
    }
    logging.info(f'log_inicial: {log_inicial}')
    for indice, linha in df.iterrows():
        saldo_total = 0
        taxas_total = 0
        ganhos_total = 0
        perdas_total = 0
        print("indice: ", indice)
        for i, indicador in enumerate(indicadores):
            
            
            sinal = indicador.calcular_sinal(linha)
            ultima_linha = (indice == (len(df) - 1))
            ativar_stop_loss = indicador.get_stop(linha['close']) or ultima_linha
            vender_bitcoin = sinal == 'Vender' or ativar_stop_loss
            if vender_bitcoin and indicador.get_estado():
                validacao = autorizar_venda(indicador, linha['close'], ativar_stop_loss, 10, 0.00001)
                if validacao:
                    quantidade_a_vender, quantidade_ativo_disponivel = validacao
                    try:
                        ordem = get_ordem_venda_simulacao(linha['close'], quantidade_a_vender)
                        if not ordem:
                            raise ValueError("Erro ao executar a ordem de venda.")
                            
                        dados_ordem = tratar_ordem(ordem, ambiente)
                        valor_operacao = dados_ordem['valor_operacao']
                        indicador.set_valor_disponivel(indicador.get_valor_disponivel() + float(valor_operacao))
                        indicador.set_quantidade_vendas(valor_operacao)
                        indicador.set_somatorio_taxas(dados_ordem['taxa_em_real'])
                        indicador.set_quantidade_bitcoin(quantidade_ativo_disponivel - float(dados_ordem['quantidade_ativo']))
                        indicador.set_estado(False)
                        log_venda = formatar_log_compra_venda(indice, indicador.nome_indicador, sinal, quantidade_ativo_disponivel, dados_ordem)
                        logging.info(f'log_venda: {log_venda}')
                    except ValueError as e:
                        logging.error(f'Erro ao vender ativo: {e}')
                        continue
            elif sinal == 'Comprar':
                if not indicador.get_estado():
                    validacao = autorizar_compra(indicador, linha['close'],  10, 0.00001)
                    if validacao:
                        quantidade_a_comprar, valor_disponivel = validacao
                        try:
                            ordem = get_ordem_compra_simulacao(linha['close'], valor_disponivel)
                            if not ordem:
                                raise ValueError("Erro ao executar a ordem de compra.")
                            
                            dados_ordem = tratar_ordem(ordem, ambiente)
                            valor_operacao = dados_ordem['valor_operacao']
                            indicador.set_quantidade_bitcoin(dados_ordem['quantidade_ativo'])
                            indicador.set_valor_ultima_compra(valor_operacao)
                            indicador.set_valor_disponivel(valor_disponivel - float(valor_operacao))
                            indicador.set_somatorio_taxas(dados_ordem['taxa_em_real'])
                            indicador.set_quantidade_compras()
                            indicador.set_estado(True)
                            log_compra = formatar_log_compra_venda(indice, indicador.nome_indicador, sinal, quantidade_a_comprar, dados_ordem)
                            logging.info(f'log_compra: {log_compra}')
                        except ValueError as e:
                            logging.error(f'Erro ao comprar ativo: {e}')
                            continue
            log_indicador = formatar_log_indicador(indicador, linha['close'])
            logging.info(f'log_indicador: {log_indicador}')
            saldo_total += log_indicador['Saldo indicador']    
            taxas_total += log_indicador['Somatorio Taxas de operacao']    
            ganhos_total += log_indicador['Somatorio ganhos']    
            perdas_total += log_indicador['Somatorio perdas']    


        log_saldo = {
                "ciclo": indice,
                "saldo": saldo_total,
                "total_taxas": taxas_total,
                "total_ganhos": ganhos_total,
                "total_perdas": perdas_total,
                "valor_bitcoin": linha['close']
        }
        logging.info(f'log_saldo: {log_saldo}')
