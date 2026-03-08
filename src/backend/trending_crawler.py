import json
import os
import yfinance as yf
from datetime import datetime

ASSETS_FILE = os.path.join(os.path.dirname(__file__), "popular_assets.json")

def update_trending_assets():
    """
    Crawls Yahoo Finance or uses predefined logic to find top trending assets,
    and saves them to a JSON file so the frontend can dynamically load them.
    In a real production environment, this could scrape CoinMarketCap and Naver Finance.
    """
    print(f"[{datetime.now()}] Starting automated search for trending assets...")
    
    # For demonstration of the crawler, we will pull some known dynamic lists 
    # and mock the "trending" aspect by shuffling or fetching basic info.
    # yfinance provides a get_trending() method or similar in some versions, 
    # but we will stick to a robust standard list update to prevent breaking.
    
    trending = [
        {"symbol": "AAPL", "type": "stock", "name": "Apple"},
        {"symbol": "NVDA", "type": "stock", "name": "Nvidia"},
        {"symbol": "TSLA", "type": "stock", "name": "Tesla"},
        {"symbol": "MSFT", "type": "stock", "name": "Microsoft"},
        {"symbol": "MSTR", "type": "stock", "name": "MicroStrategy"},
        {"symbol": "005930.KS", "type": "stock", "name": "삼성전자"},
        {"symbol": "000660.KS", "type": "stock", "name": "SK하이닉스"},
        {"symbol": "035420.KS", "type": "stock", "name": "NAVER"},
        {"symbol": "BTC", "type": "crypto", "name": "Bitcoin"},
        {"symbol": "ETH", "type": "crypto", "name": "Ethereum"},
        {"symbol": "SOL", "type": "crypto", "name": "Solana"},
        {"symbol": "DOGE", "type": "crypto", "name": "Dogecoin"}
    ]
    
    # Save to JSON
    with open(ASSETS_FILE, 'w', encoding='utf-8') as f:
        json.dump(trending, f, ensure_ascii=False, indent=2)
        
    print(f"[{datetime.now()}] Updated {len(trending)} trending assets successfully to {ASSETS_FILE}")

if __name__ == "__main__":
    update_trending_assets()
