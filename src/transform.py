import logging
import pandas as pd
import os


logger = logging.getLogger(__name__)


def transform_stock_data(raw_df):
    if raw_df.empty :
        logging.warning("Input DataFrame is empty. Skipping transform.")
        return pd.DataFrame(),pd.DataFrame()
    df = raw_df.copy()
    required_cols = ["ticker","trade_date","open","high","low","close","volume"]

    cond_null = df[required_cols].isna().any(axis=1)

    cond_non_positive = df["close"] <= 0

    cond_dup = df.duplicated(subset = ["ticker","trade_date"],keep="first")

    cond_high_low  = df["high"] < df["low"]

    invalid_mask = cond_null | cond_non_positive | cond_dup | cond_high_low

    rejected_df = df[invalid_mask].copy()
    clean_df = df[~invalid_mask].copy()

    if not rejected_df.empty :
        os.makedirs("data", exist_ok=True)
        rejected_df.to_csv("data/rejected_rows.csv",index=False)

    clean_df = clean_df.sort_values(["ticker","trade_date"]).reset_index(drop=True)

    clean_df["daily_return"] = clean_df.groupby("ticker")["close"].pct_change()
    clean_df["sma_20"] = clean_df.groupby("ticker")["close"].transform(
        lambda s : s.rolling(window=20).mean()
    )
    logger.info(f"Transform complete : {len(clean_df)} clean rows, {len(rejected_df)} rejected rows")

    return clean_df,rejected_df

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    sample_df = pd.DataFrame([
        # แถวดี 2 แถว (จะได้เช็ก daily_return ด้วย)
        {"ticker": "AAPL", "trade_date": "2026-11-01", "open": 100.0, "high": 105.0, "low": 99.0, "close": 100.0, "volume": 1000},
        {"ticker": "AAPL", "trade_date": "2026-11-02", "open": 101.0, "high": 110.0, "low": 100.0, "close": 105.0, "volume": 1200},
        # แถวเสีย 1: มีค่าว่าง (None/NaN)
        {"ticker": "AAPL", "trade_date": "2026-11-03", "open": None,  "high": 110.0, "low": 100.0, "close": 105.0, "volume": 1200},
        # แถวเสีย 2: ราคาปิดติดลบ (close <= 0)
        {"ticker": "AAPL", "trade_date": "2026-11-04", "open": 100.0, "high": 105.0, "low": 95.0,  "close": -10.0, "volume": 1200},
        # แถวเสีย 3: หุ้นและวันที่ซ้ำกับแถวแรก
        {"ticker": "AAPL", "trade_date": "2026-11-01", "open": 100.0, "high": 105.0, "low": 99.0,  "close": 100.0, "volume": 1000},
        # แถวเสีย 4: High ต่ำกว่า Low
        {"ticker": "AAPL", "trade_date": "2026-11-05", "open": 100.0, "high": 90.0,  "low": 105.0, "close": 100.0, "volume": 1200},
    ])

    clean, rejected = transform_stock_data(sample_df)
    print("\n--- CLEAN ---")
    print(clean[["ticker", "trade_date", "close", "daily_return", "sma_20"]])
    print("\n--- REJECTED ---")
    print(rejected[["ticker", "trade_date", "open", "high", "low", "close"]])



    

    