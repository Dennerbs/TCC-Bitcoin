import logging

def configurar_logger(nome_arquivo):
    # Define o nome do arquivo de log baseado no nome da função
    arquivo_log = nome_arquivo
    
    # Configura o basicConfig com o arquivo de log dinâmico
    logging.basicConfig(filename=arquivo_log,
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')