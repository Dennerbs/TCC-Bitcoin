from binance.client import Client
import pandas as pd
import pytz
import os
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("API_KEY_BINACE")
api_secret = os.getenv("API_SECRET_BINACE")

client = Client(api_key, api_secret)

# Função para obter dados de mercado ao vivo
def get_dados_criptomoeda(intervalo='1h', simbolo = 'BTCUSDT'):
    klines = client.get_klines(symbol=simbolo, interval=intervalo)
    
    df = pd.DataFrame(klines, columns=[
        'timestamp', 'open', 'high', 'low', 'close', 'volume', 
        'close_time', 'quote_asset_volume', 'number_of_trades', 
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    
    timezone = pytz.timezone('America/Campo_Grande')
    df['timestamp'] = df['timestamp'].dt.tz_localize('UTC').dt.tz_convert(timezone)
    
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
    
    df[['open', 'high', 'low', 'close', 'volume']] = df[['open', 'high', 'low', 'close', 'volume']].astype(float)
    
    df.rename(columns={'timestamp': 'date'}, inplace=True)

    return df

def get_linha(intervalo, simbolo):
    df = get_dados_criptomoeda(intervalo=intervalo, simbolo=simbolo)
    return df.iloc[-1]

def tempo_intervalo(intervalo):
    unit = intervalo[-1]
    if unit == 'm':
        return int(intervalo[:-1]) * 60
    elif unit == 'h':
        return int(intervalo[:-1]) * 3600
    elif unit == 'd':
        return int(intervalo[:-1]) * 86400
    elif unit == 'w':
        return int(intervalo[:-1]) * 604800
    elif unit == 'M':
        return int(intervalo[:-1]) * 2592000

