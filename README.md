# Web Scraping e Regressão Linear — Previsão de Preços de Imóveis

Projeto em Python que coleta anúncios de apartamentos para aluguel em São Paulo (QuintoAndar) via web scraping e aplica modelos de regressão linear para prever o preço dos imóveis.

## Funcionalidades

1. **Web Scraping** – usa Selenium (Firefox em modo headless) para coletar os anúncios e salvar os dados em CSV.
2. **Regressão Linear** – limpeza dos dados, remoção de outliers (IQR), análise exploratória (EDA), análise OLS, VIF, e comparação entre Regressão Linear Múltipla, Ridge e Lasso.

## Requisitos

- Python 3.11+
- Navegador **Mozilla Firefox** instalado (necessário para o web scraping)

### Bibliotecas necessárias

| Biblioteca     | Uso                                              |
|----------------|--------------------------------------------------|
| `selenium`     | Automação do navegador para o web scraping       |
| `pandas`       | Manipulação e limpeza dos dados                  |
| `numpy`        | Operações numéricas                              |
| `matplotlib`   | Geração de gráficos                              |
| `seaborn`      | Gráficos estatísticos (EDA)                      |
| `statsmodels`  | Regressão OLS e cálculo de VIF                   |
| `scikit-learn` | Modelos de regressão, divisão treino/teste e métricas |

As versões testadas estão em [requirements.txt](requirements.txt).

## Instalação

```bash
# Clonar o repositório
git clone <url-do-repositorio>
cd imobliaria

# Criar e ativar o ambiente virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS

# Instalar as dependências
pip install -r requirements.txt
```

Ou, instalando manualmente:

```bash
pip install selenium pandas numpy matplotlib seaborn statsmodels scikit-learn
```

## Como executar

```bash
python main.py
```

Escolha uma opção no menu:

- `1` – Coleta os dados dos imóveis e salva em um arquivo CSV.
- `2` – Executa a análise de regressão linear sobre o CSV.

> **Observação:** a opção 2 lê o arquivo `data_propriety copy.csv` da raiz do projeto (o caminho é resolvido a partir da pasta do `main.py`, então funciona em qualquer máquina).

## Estrutura

```
├── main.py
├── data_propriety.csv
├── data_propriety copy.csv
└── src/Modules/WebData/
    ├── Application/Services/
    │   ├── webDataService.py           # Web scraping com Selenium
    │   └── LinearRegressionService.py  # Análise e modelos de regressão
    └── Infrastructure/Repositories/
        └── webDataRepository.py        # Gravação dos dados em CSV
```
