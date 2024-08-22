from API.binance_api import get_dados_criptomoeda, tempo_intervalo, get_dados_bitcoin_websocket, get_valores_minimos_operacao, comprar_ativo, vender_ativo, tratar_ordem
from Utils.utils import calibrar_df_indicadores, formatar_log_compra_venda, formatar_log_indicador
import logging
import asyncio

async def trade(indicadores, valor_total, intervalo='1h', simbolo='BTCBRL'):
    df_inicial = get_dados_criptomoeda(intervalo)
    calibrar_df_indicadores(indicadores, df_inicial=df_inicial)
    intervalo_em_segundo = tempo_intervalo(intervalo)
    valor_minimo_negociacao, quantidade_minima_ativo = get_valores_minimos_operacao(simbolo)

    await asyncio.sleep(intervalo_em_segundo)
    contador = 0

    while True:
        contador += 1
        print(f'Ciclo: {contador}')
        saldo_total = 0
        taxas_total = 0
        ganhos_total = 0
        perdas_total = 0
        linha = await get_dados_bitcoin_websocket('btcbrl', intervalo)
        
        for indicador in indicadores:
            sinal = indicador.calcular_sinal(linha)
            
            parar_perda = indicador.get_stop(linha['close'])
            vender_bitcoin = sinal == 'Vender' or parar_perda
            if vender_bitcoin and indicador.get_estado():
                valor_venda = indicador.get_quantidade_bitcoin() * linha['close']
                taxa_transacao = valor_venda * 0.001
                lucro_potencial = valor_venda - taxa_transacao
                valor_ultima_compra = indicador.get_valor_ultima_compra()
                lucro_minimo = valor_ultima_compra * indicador.get_lucro_minimo_venda()
                if parar_perda or (sinal == 'Vender' and lucro_potencial > valor_minimo_negociacao and lucro_potencial > lucro_minimo):
                    indicador.set_estado(False)
                    quantidade_bitcoin = indicador.get_quantidade_bitcoin()
                    try:
                        ordem = vender_ativo(quantidade_bitcoin, quantidade_minima_ativo)
                        dados_ordem = tratar_ordem(ordem)
                        valor_operacao = dados_ordem['valor_operacao']
                        indicador.set_valor_disponivel(valor_operacao)
                        indicador.set_quantidade_vendas(valor_operacao)
                        indicador.set_somatorio_taxas(dados_ordem['taxa_em_real'])
                        indicador.set_quantidade_bitcoin(0)
                        log_venda = formatar_log_compra_venda(contador, indicador.nome_indicador, sinal, quantidade_bitcoin, dados_ordem, valor_operacao)
                        logging.info(f'log_venda: {log_venda}')
                    except Exception as e:
                        logging.error(f'Erro ao vender ativo ou tratar ordem: {e}')
                        continue
            elif sinal == 'Comprar':
                if not indicador.get_estado():
                    indicador.set_quantidade_compras()
                    indicador.set_estado(True)
                    valor_disponivel = indicador.get_valor_disponivel()
                    if valor_disponivel < valor_minimo_negociacao:
                        logging.info(f'log_indisponibilidade: Sem valor minimo para negociar')
                        continue
                    try:
                        quantidade_a_comprar =  valor_disponivel / linha['close']
                        ordem = comprar_ativo(quantidade_a_comprar, quantidade_minima_ativo)
                        dados_ordem = tratar_ordem(ordem)
                        valor_operacao = dados_ordem['valor_operacao']
                        indicador.set_quantidade_bitcoin(dados_ordem['quantidade_ativo'])
                        indicador.set_valor_ultima_compra(valor_operacao)
                        indicador.set_valor_disponivel(0)
                        indicador.set_somatorio_taxas(dados_ordem['taxa_em_real'])
                        log_compra = formatar_log_compra_venda(contador, indicador.nome_indicador, sinal, quantidade_a_comprar, dados_ordem, valor_operacao)
                        logging.info(f'log_compra: {log_compra}')
                    except Exception as e:
                        logging.error(f'Erro ao comprar ativo ou tratar ordem: {e}')
                        continue
            log_indicador = formatar_log_indicador(indicador, linha['close'])
            logging.info(f'log_indicador: {log_indicador}')
            saldo_total += log_indicador['Saldo indicador']    
            taxas_total += log_indicador['Somatorio Taxas de operacao']    
            ganhos_total += log_indicador['Somatorio ganhos']    
            perdas_total += log_indicador['Somatorio perdas']    
  

        log_saldo = {
                "ciclo": contador,
                "saldo": saldo_total,
                "total_taxas:": taxas_total,
                "total_ganhos": ganhos_total,
                "total_perdas": perdas_total,
                "valor_bitcoin": linha['close']
        }
        logging.info(f'log_saldo: {log_saldo}')
