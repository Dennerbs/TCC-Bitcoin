# Projeto TCC
## Pré-requisitos

- Python 3
- pip (gerenciador de pacotes Python)
- Conta na Binance (para modo produção)
- Conta na Binance Testnet (para modo teste)
- Dataset com dados do bitcoin

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/Dennerbs/TCC-Bitcoin.git
cd TCC-Bitcoin
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Configuração

### Dataset para Simulação

Para utilizar o módulo de simulação, você precisa:

1. Baixar o dataset de preços do Bitcoin [neste link do Kaggle](https://www.kaggle.com/datasets/kaanxtr/btc-price-1m/data)
2. Colocar o arquivo CSV na pasta `Dados` com o nome `BTC-2024min.csv`

### Configuração das APIs

#### Modo Produção
Para usar execução em tempo real na produção, você precisa:
1. Ter uma conta ativa na [Binance](https://www.binance.com)
2. Criar uma API key e Secret key no seu painel da Binance
3. Configurar essas chaves no arquivo `.env`

#### Modo Teste
Para usar execução em tempo real em teste, você precisa:
1. Se registrar na [Binance Testnet](https://testnet.binance.vision)
2. Criar uma API key e Secret key na testnet
3. Configurar essas chaves no arquivo `.env`

### Arquivo .env

Crie um arquivo `.env` na raiz do projeto com o seguinte formato:

```env
#TESTE ou PRINCIPAL
AMBIENTE='TESTE'

#principal
API_KEY_BINACE= 
API_SECRET_BINACE=

#teste
API_KEY_BINACE_TEST= 
API_SECRET_BINACE_TEST=
```

## Execução

Para iniciar o sistema:
```bash
python main.py
```

## Modo de Uso
- Para simulação: Configure a função `rodar_simulacao()` dentro da função `main()` no arquivo `main.py` e certifique-se de que o dataset está corretamente posicionado
- Para produção: Configure o ambiente como 'PRINCIPAL' no `.env`, coloque a função `rodar_ao_vivo()` dentro da função `main()` no arquivo `main.py` e insira suas chaves de API da Binance
- Para teste: Mantenha o ambiente como 'TESTE', coloque a função `rodar_ao_vivo()` dentro da função `main()` no arquivo `main.py` e use as chaves da Testnet
