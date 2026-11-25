import logging 
from datetime import datetime 
import yfinance as yf
import pandas as pd
import os 

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/etl.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def extract_stock_data(tickers,period="1mo"):
    all_data =[]

    for ticker in tickers :
        try :
            logging.info(f"Fetching {ticker}:")
            df = yf.Ticker(ticker).history(period=period)
            if df.empty:
                logging.warning(f"No data found for {ticker}")
                continue
            df = df.reset_index()
            df = df[["Date", "Open", "High", "Low", "Close", "Volume"]].copy()
            df = df.rename(columns={
                        "Date": "trade_date",
                        "Open": "open",
                        "High": "high",
                        "Low": "low",
                        "Close": "close",
                        "Volume": "volume",
                    })
            df["trade_date"] = pd.to_datetime(df["trade_date"],utc=True).dt.strftime("%Y-%m-%d")
            df["ticker"] = ticker
            df["ingested_at"] = datetime.now().isoformat()
            all_data.append(df)
            logging.info(f"Fetched {len(df)} rows for {ticker}")  
        except Exception as e:
            logging.error(f"Error fetching {ticker}: {e}")

    if all_data :
        return pd.concat(all_data,ignore_index=True)
    else :
        logging.warning("No data extracted for any ticker.")
        return pd.DataFrame()
    
if __name__ == "__main__":
    sample_tickers = ["AAPL", "MSFT", "BBL.BK", "INVALID123"]
    result = extract_stock_data(sample_tickers, period="1mo")
    print(result.head())
    print(f"Total rows: {len(result)}")
     