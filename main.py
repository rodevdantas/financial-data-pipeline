import logging
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from googleapiclient.discovery import build
import traceback

# %%

# Exibe um resumo formatado de um DataFrame para o log.
def describe_dataframe_short(df: pd.DataFrame, name: str = "df"):
    logging.info(f"=== Descrição resumida de {name} ===")
    logging.info(f"shape: {df.shape}")
    logging.info(f"columns (first 50): {list(df.columns)[:50]}")
    logging.info("dtypes:")
    logging.info(df.dtypes.astype(str).to_dict())
    tuple_cols = [c for c in df.columns if isinstance(c, tuple)]
    if tuple_cols:
        logging.warning(f"Colunas com nomes em formato tuple detectadas: {tuple_cols}")
    logging.info("preview (5 rows):")
    
    preview_df = df.head(5).astype(str)
    
    logging.info(preview_df.to_dict(orient='list'))

# Extrai dados históricos de ações do Yahoo Finance para a camada Bronze.
def extract_to_bronze() -> pd.DataFrame:
    logging.info("Iniciando extração e salvando na camada Bronze.")
    
    TOP_STOCKS_TICKERS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'BRK-B', 'JPM', 'JNJ']
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    try:
        raw_data = yf.download(
            " ".join(TOP_STOCKS_TICKERS),
            start=start_date,
            end=end_date,
            auto_adjust=False,
            progress=False,
            group_by='ticker'
        )

        if raw_data.empty:
            logging.warning("Nenhum dado retornado. Abortando.")
            return pd.DataFrame()

        df_bronze = raw_data.stack(level=0).reset_index()
        df_bronze = df_bronze.rename(columns={'level_1': 'Ticker', 'Adj Close': 'Adj_Close'})

        df_bronze['Date'] = pd.to_datetime(df_bronze['Date'], errors='coerce')
        df_bronze.dropna(subset=['Date'], inplace=True)
        
        logging.info(f"Extração concluída. Total de linhas: {len(df_bronze)}")
        return df_bronze

    except Exception as e:
        logging.error(f"Erro ao extrair dados: {e}")
        return pd.DataFrame()

# Converte o DataFrame para uma matriz de valores compatível com o Google Sheets.
def dataframe_to_sheets_values(df: pd.DataFrame) -> list[list]:
    """Converte um DataFrame para uma matriz de valores 100% serializável em JSON/Sheets."""
    df2 = df.copy()

    if 'Date' in df2.columns:
        df2['Date'] = pd.to_datetime(df2['Date'], errors='coerce').dt.strftime('%Y-%m-%d')

    df2 = df2.astype(object).where(pd.notnull(df2), '')

    def to_builtin(x):
        try:
            return x.item()
        except Exception:
            return x

    for c in df2.columns:
        df2[c] = df2[c].map(to_builtin)

    return [df2.columns.tolist()] + df2.values.tolist()

# Aplica transformações de limpeza e de preços para a camada Silver.
def transform_to_silver(df_bronze: pd.DataFrame) -> pd.DataFrame:
    logging.info("Iniciando transformação e salvando na camada Silver.")
    df_silver = df_bronze.copy()
    
    if df_silver.empty:
        return df_silver
    
    required = ['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj_Close']
    for col in required:
        if col not in df_silver.columns:
            df_silver[col] = pd.NA
            
    df_silver['Volume'] = pd.to_numeric(df_silver['Volume'], errors='coerce').fillna(0).astype(int)
    for col in ['Open', 'High', 'Low', 'Close', 'Adj_Close']:
        df_silver[col] = pd.to_numeric(df_silver[col], errors='coerce').fillna(0)
    
    if 'Adj_Close' in df_silver.columns and 'Close' in df_silver.columns and not df_silver['Close'].isnull().all():
        df_silver['Adj_Close_Ratio'] = df_silver['Adj_Close'] / df_silver['Close']
        df_silver['Open'] *= df_silver['Adj_Close_Ratio']
        df_silver['High'] *= df_silver['Adj_Close_Ratio']
        df_silver['Low'] *= df_silver['Adj_Close_Ratio']
        df_silver['Close'] = df_silver['Adj_Close']
        df_silver = df_silver.drop(columns=['Adj_Close', 'Adj_Close_Ratio'], errors='ignore')
    
    df_silver.fillna(0, inplace=True)
    return df_silver

# Cria a camada Gold com uma coluna a mais = variação diária em porcentagem.
def create_gold_table(df_silver: pd.DataFrame) -> pd.DataFrame:
    logging.info("Iniciando criação da camada Gold.")
    df_gold = df_silver.copy()

    if df_gold.empty:
        return df_gold
    
    df_gold = df_gold.sort_values(['Ticker', 'Date']).reset_index(drop=True)
    
    df_gold['Daily_Change_Pct'] = df_gold.groupby('Ticker')['Close'].pct_change() * 100
    df_gold['Daily_Change_Pct'].fillna(0, inplace=True)
    
    colunas_finais = ['Ticker', 'Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Daily_Change_Pct']
    df_gold = df_gold[colunas_finais]

    return df_gold

# Envia os dados processados para uma aba específica do Google Sheets.
def load_data_to_sheets(dataframe: pd.DataFrame, sheet_id: str, sheet_tab: str = 'Stocks_Data'):
    logging.info("Carregando dados para o Google Sheets via API...")
    try:
        service = build('sheets', 'v4', cache_discovery=False)

        data_to_upload = dataframe_to_sheets_values(dataframe)

        range_name = f"{sheet_tab}!A1"

        body = {'values': data_to_upload}

        result = service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        logging.info(f"Dados carregados para o Google Sheets com sucesso. Células atualizadas: {result.get('updatedCells')}")
    except Exception as e:
        logging.exception(f"Erro ao carregar dados para o Google Sheets: {e}")
        raise

# %%

# Ponto de entrada principal do Cloud Function que orquestra todo o pipeline.
def main(request):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    try:
        logging.info("Requisição HTTP recebida. Iniciando pipeline.")

        SHEET_ID = "1H779bzHVLrPaaHEuLEIRsJt1OdSXKBu02GmlhST2EjI" 
        
        df_bronze = extract_to_bronze()
        df_silver = transform_to_silver(df_bronze)
        df_gold = create_gold_table(df_silver)
        
        if not df_gold.empty:
            logging.info(f"df_gold max Date: {df_gold['Date'].max()}, rows: {len(df_gold)}")
            describe_dataframe_short(df_gold, "Camada Gold")
            load_data_to_sheets(df_gold, SHEET_ID, sheet_tab='Stocks_Data')
        else:
            logging.warning("DataFrame Gold vazio. Nenhuma carga foi realizada.")

        logging.info("Fluxo ETL e carga para Sheets concluídos.")
        
        return "Pipeline executado com sucesso!"
    except Exception as e:
        logging.exception("Erro durante a execução do pipeline.")
        return f"Erro no pipeline: {traceback.format_exc()}"