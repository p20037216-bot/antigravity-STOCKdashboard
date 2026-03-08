import pandas as pd
import numpy as np

def apply_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply common technical indicators using pure pandas.
    Includes moving averages (SMA), RSI, and Bollinger Bands.
    """
    if df is None or df.empty:
        return df
        
    close = df['close']
    
    # Moving Averages using SMA
    df['SMA_20'] = close.rolling(window=20).mean()
    df['SMA_50'] = close.rolling(window=50).mean()
    df['SMA_200'] = close.rolling(window=200).mean()
    
    # RSI (14 period)
    delta = close.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI_14'] = 100 - (100 / (1 + rs))
    
    # Bollinger Bands (20 period, 2 std)
    df['BBL_20_2.0'] = df['SMA_20'] - (close.rolling(window=20).std() * 2)
    df['BBU_20_2.0'] = df['SMA_20'] + (close.rolling(window=20).std() * 2)
    
    # Clean up NaN values resulting from indicator calculation
    df.dropna(inplace=True)
    return df
