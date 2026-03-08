import yfinance as yf
import ccxt
import pandas as pd
from datetime import datetime, timedelta

def get_stock_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """Download historical stock data from Yahoo Finance."""
    try:
        # Download data
        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            return data
            
        # Flatten multiindex columns from newer yfinance versions if needed
        if hasattr(data.columns, 'levels') and 'Ticker' in data.columns.names:
            data = data.xs(ticker, level='Ticker', axis=1)
            
        # Rename columns to standard format
        data = data.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        })
        return data
    except Exception as e:
        print(f"Error downloading stock data for {ticker}: {e}")
        return pd.DataFrame()

def get_crypto_data(symbol: str, timeframe: str = '1d', limit: int = 1825) -> pd.DataFrame:
    """Download historical crypto data from Binance via CCXT. 1825 days is approx 5 years."""
    try:
        exchange = ccxt.binance()
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['Date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('Date', inplace=True)
        df.drop('timestamp', axis=1, inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching crypto data for {symbol}: {e}")
        return None

def get_valuation_metrics(symbol: str) -> dict:
    """Fetch fundamental valuation metrics from Yahoo Finance."""
    try:
        if "/" in symbol or "BTC" in symbol or "ETH" in symbol:
            return {"symbol": symbol, "error": "Crypto assets do not have traditional fundamentals"}
            
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "fwd_per": info.get("forwardPE", 0),
            "ttm_per": info.get("trailingPE", 0),
            "pbr": info.get("priceToBook", 0),
            "psr": info.get("priceToSalesTrailing12Months", 0),
            "ev_ebitda": info.get("enterpriseToEbitda", 0),
            "dividend_yield": info.get("dividendYield", 0) * 100 if info.get("dividendYield") else 0,
            "roe": info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") else 0,
        }
    except Exception as e:
        print(f"Error fetching fundamental for {symbol}: {e}")
        return {"symbol": symbol, "error": "Fetch failed"}

# You can add FRED macro data collection here later once an API key is provided
