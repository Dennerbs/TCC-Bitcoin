
import matplotlib
matplotlib.use('TkAgg',force=True)
from matplotlib import pyplot as plt
from datetime import datetime, timedelta
from matplotlib.dates import DateFormatter
def tomar_decisao_RSI(rsi_valor, topo, baixa):
    if rsi_valor > topo:
        return "Vender"  
    elif rsi_valor < baixa:
        return "Comprar"  
    else:
        return "Manter"  

##################################################

#RSI

def calcular_diferenca(df):
    df = df.copy()
    df['diferenca'] = df['close'].diff()

    return df

def calcular_ganho_perda(df):
    df['ganho'] = 0
    df['perda'] = 0


    for i in range(1, len(df)):
        diferenca = df.at[i, 'diferenca']
        if diferenca > 0:
            df.at[i, 'ganho'] = diferenca
        else:
            df.at[i, 'perda'] = abs(diferenca)

    return df

def calcular_media_ganho_perda(df, periodo):
    df['media_ganho'] = 0
    df['media_perda'] = 0

    for i in range(1, len(df)):
        if i < periodo:
            # Calcula a média simples das primeiras 'i' linhas
            media_ganho = df['ganho'][:i].mean()
            media_perda = df['perda'][:i].mean()
        else:
            # Calcula a média ponderada a partir do período definido
            media_ganho = ((df['media_ganho'][i - 1] * (periodo - 1)) + df['ganho'][i]) / periodo
            media_perda = ((df['media_perda'][i - 1] * (periodo - 1)) + df['perda'][i]) / periodo

        df.at[i, 'media_ganho'] = media_ganho
        df.at[i, 'media_perda'] = media_perda

    return df

def calcular_rsi(df):
    for i in range(len(df)):
        media_ganho = df.at[i, 'media_ganho']
        media_perda = df.at[i, 'media_perda']

        if media_perda == 0:
            rs = 0
        else:
            rs = media_ganho / media_perda

        rsi = 100 - (100 / (1 + rs))
        df.at[i, 'rsi'] = rsi

    return df

def imprimir_rsi(df, topo, baixo):
    df['decisao'] = "";
    for i in range(len(df)):
        rsi = df.at[i, 'rsi']
        decisao = tomar_decisao_RSI(rsi, topo, baixo)
        df.at[i, 'decisao'] = decisao;
        #print(f'RSI da linha {i}: {rsi} - {decisao}')

    return df


def graficoRSI(df, topo, baixo):
    df['rsi'] = df['rsi'].astype(float) 
    
    delta = timedelta(hours=24)
    start_date = df.at[0, 'date'].to_pydatetime()
    #dates = [start_date + i * delta for i in range(len(df))]
    plt.figure(figsize=(10, 5))
    plt.plot(df['date'], df['rsi'], label='RSI', color='blue')
    plt.axhline(topo, color='r', linestyle='--', label=f'Topo ({topo})')
    plt.axhline(baixo, color='g', linestyle='--', label=f'Baixa ({baixo})')
    
    plt.title('Gráfico de RSI')
    plt.xlabel('Data')
    plt.ylabel('RSI')
    
    date_format = DateFormatter("%Y-%m-%d")
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.gcf().autofmt_xdate()
    
    plt.legend()
    plt.show()
       
##################################################



# Periodo  | Topo | baixa | Lucro
# 5(dias)  |  70  | 30    |  204.64
# 5(dias)  |  80  | 50    |  400.99

# 7(dias)  |  80  | 50    |  452.73

# 10(dias)  |  70  | 30   |  15.63
# 10(dias)  |  80  | 50   |  741.18

# 12(dias)  |  70  | 30   |  -200.51
# 12(dias)  |  80  | 50   |  1326.61

# 14(dias) |  60  | 50    |  177.77
# 14(dias) |  70  | 30    |  122.48
# 14(dias) |  70  | 40    |  -158.85
# 14(dias) |  70  | 50    |  510.17
# 14(dias) |  70  | 60    |  406.31
# 14(dias) |  80  | 40    |  8.66
# 14(dias) |  80  | 50    |  775.12
# 14(dias) |  80  | 60    |  516.49
# 14(dias) |  80  | 70    |  603.25