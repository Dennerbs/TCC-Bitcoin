import logging
from logging.handlers import RotatingFileHandler

def configurar_logger(nome_arquivo, max_bytes=23000000, backup_count=20):
    arquivo_log = nome_arquivo

    handler = RotatingFileHandler(arquivo_log, maxBytes=max_bytes, backupCount=backup_count, delay=False)
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

