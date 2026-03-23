from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from .data_collector import get_stock_data, get_crypto_data, get_valuation_metrics
from .indicators import apply_indicators
from .backtester import run_backtest
from .ai_reporter import generate_investment_report, summarize_global_news, generate_analyst_report
from .news_crawler import get_global_news
from .macro_data import get_all_macro_data, FALLBACK_DATA
import pandas as pd
from datetime import datetime, timedelta
import dotenv
import math
import os
import time
import logging

# Load environment variables
dotenv.load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Antigravity Finance Dashboard API")

# Simple In-Memory Cache with TTL
class SimpleCache:
    def __init__(self, ttl_seconds=3600):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key):
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                return entry['data']
            else:
                del self.cache[key]
        return None

    def set(self, key, data):
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

# Initialize caches
analyze_cache = SimpleCache(ttl_seconds=3600)  # 1 hour
news_cache = SimpleCache(ttl_seconds=1800)     # 30 mins
overview_cache = SimpleCache(ttl_seconds=600)  # 10 mins
macro_cache = SimpleCache(ttl_seconds=3600)    # 1 hour

app.add_middleware(
    CORSMiddleware,
    # In production, this should be restricted to the specific frontend domain
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/analyze/{asset_type}/{symbol}")
async def analyze_asset(asset_type: str, symbol: str):
    """
    Analyzes an asset (stock/crypto) over 5 years.
    Returns indicators, backtest results, and AI analysis.
    """
    cache_key = f"analyze_{asset_type}_{symbol}"
    cached_res = analyze_cache.get(cache_key)
    if cached_res:
        logger.info(f"Returning cached analysis for {symbol}")
        return cached_res

    try:
        # 1. Collect Data
        if asset_type.lower() == "stock":
            end = datetime.now()
            start = end - timedelta(days=1825)
            df = get_stock_data(symbol, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        elif asset_type.lower() == "crypto":
            symbol_formatted = symbol if "/" in symbol else f"{symbol}/USDT"
            df = get_crypto_data(symbol_formatted)
        else:
            raise HTTPException(status_code=400, detail="Invalid asset type. Use 'stock' or 'crypto'.")
            
        if df is None or df.empty:
            raise HTTPException(status_code=404, detail=f"Could not fetch data for {symbol}")
            
        # 2. Add technical indicators
        df_with_indicators = apply_indicators(df.copy())
        
        # 3. Run Backtest
        backtest_results = run_backtest(df.copy())
        
        # 4. Generate AI Report
        df_clean = df_with_indicators.fillna(0)
        
        for col in df_clean.select_dtypes(include=['float']).columns:
            df_clean[col] = df_clean[col].apply(lambda x: 0.0 if math.isnan(x) or math.isinf(x) else x)

        latest_data = df_clean.iloc[-1].to_dict()
        
        if 'Date' in latest_data and isinstance(latest_data['Date'], pd.Timestamp):
            latest_data['Date'] = latest_data['Date'].strftime('%Y-%m-%d')
            
        ai_report = generate_investment_report(symbol, latest_data, backtest_results)
        
        chart_data = df_clean.tail(100).reset_index()
        if 'Date' in chart_data.columns:
            chart_data['Date'] = chart_data['Date'].dt.strftime('%Y-%m-%d')
            
        records = chart_data.to_dict(orient='records')
        
        result = {
            "symbol": symbol,
            "type": asset_type,
            "backtest_metrics": backtest_results,
            "ai_analysis": ai_report,
            "chart_data": records
        }
        
        analyze_cache.set(cache_key, result)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing {symbol}: {e}")
        # Avoid leaking raw exception details to the client
        raise HTTPException(status_code=500, detail="An internal error occurred during analysis.")

@app.get("/api/news")
async def get_news_summary():
    """Fetches latest news and returns an AI summary."""
    cached_news = news_cache.get("global_news")
    if cached_news:
        return cached_news

    try:
        news_data = get_global_news()
        ai_summary = summarize_global_news(news_data)
        result = {
            "raw_news": news_data,
            "ai_summary": ai_summary
        }
        news_cache.set("global_news", result)
        return result
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market news.")

@app.get("/api/overview")
async def get_market_overview():
    """Gets a quick overview of predefined major assets (Stocks + Crypto)."""
    cached_overview = overview_cache.get("market_overview")
    if cached_overview:
        return cached_overview

    assets = [
        {"symbol": "AAPL", "type": "stock"},
        {"symbol": "TSLA", "type": "stock"},
        {"symbol": "NVDA", "type": "stock"},
        {"symbol": "BTC", "type": "crypto"},
        {"symbol": "ETH", "type": "crypto"},
        {"symbol": "SOL", "type": "crypto"},
    ]
    
    results = []
    end = datetime.now()
    start = end - timedelta(days=1825)
    
    for asset in assets:
        try:
            if asset["type"] == "stock":
                df = get_stock_data(asset["symbol"], start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
            else:
                df = get_crypto_data(asset["symbol"])
                
            if df is not None and not df.empty:
                df_with_indicators = apply_indicators(df.copy())
                backtest_results = run_backtest(df.copy())
                
                latest = df_with_indicators.iloc[-1].fillna(0)
                price = float(latest.get('close', 0))
                sma20 = float(latest.get('SMA_20', 0))
                sma50 = float(latest.get('SMA_50', 0))
                rsi = float(latest.get('RSI_14', 50))
                
                signal = "HOLD"
                if sma20 > sma50 and rsi < 70:
                    signal = "BUY"
                elif sma20 < sma50 or rsi > 70:
                    signal = "SELL"
                
                results.append({
                    "symbol": asset["symbol"],
                    "type": asset["type"],
                    "price": price,
                    "signal": signal,
                    "win_rate": backtest_results.get("win_rate_pct", 0),
                    "total_return": backtest_results.get("total_return_pct", 0)
                })
        except Exception as e:
            logger.warning(f"Skipping {asset['symbol']} due to error: {e}")
            
    result = {"overview": results}
    overview_cache.set("market_overview", result)
    return result

@app.post("/api/compare/chart")
async def compare_charts(payload: Dict[str, Any] = Body(...)):
    """Accepts a list of symbols and a timeframe, returning synchronized percentage returns."""
    symbols = payload.get("symbols", [])
    start_date_str = payload.get("start_date")
    end_date_str = payload.get("end_date")
    
    if not symbols:
        raise HTTPException(status_code=400, detail="No symbols provided")
        
    if end_date_str:
        end = datetime.strptime(end_date_str, '%Y-%m-%d')
    else:
        end = datetime.now()
        
    if start_date_str:
        start = datetime.strptime(start_date_str, '%Y-%m-%d')
    else:
        start = end - timedelta(days=1095) # Default 3 years
    
    combined_data = {}
    
    for asset in symbols:
        sym = asset.get('symbol')
        asset_type = asset.get('type')
        
        try:
            if asset_type == 'stock':
                df = get_stock_data(sym, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
            else:
                df = get_crypto_data(sym)
                df = df[df.index >= start]
            
            if df is not None and not df.empty:
                base_price = df['close'].iloc[0]
                df['pct_return'] = ((df['close'] - base_price) / base_price) * 100
                
                for date, row in df.iterrows():
                    date_str = date.strftime('%Y-%m-%d')
                    if date_str not in combined_data:
                        combined_data[date_str] = {"date": date_str}
                    
                    combined_data[date_str][sym] = 0.0 if math.isnan(row['pct_return']) else float(row['pct_return'])
        except Exception as e:
            logger.error(f"Error processing {sym} for chart compare: {e}")
            
    sorted_records = [combined_data[d] for d in sorted(combined_data.keys())]
    return {"chart_data": sorted_records}

@app.post("/api/compare/valuation")
async def compare_valuations(payload: Dict[str, Any] = Body(...)):
    """Accepts a list of symbols and returns their fundamental valuation metrics."""
    symbols = payload.get("symbols", [])
    
    if not symbols:
        raise HTTPException(status_code=400, detail="No symbols provided")
        
    results = []
    for asset in symbols:
        sym = asset.get('symbol')
        asset_type = asset.get('type')
        
        if asset_type == 'crypto':
             results.append({"symbol": sym, "error": "Crypto assets do not have traditional fundamentals"})
        else:
            metrics = get_valuation_metrics(sym)
            results.append(metrics)
            
    return {"valuations": results}

@app.get("/api/macro")
async def get_macro_indicators():
    """Fetches macroeconomic indicators."""
    cached_macro = macro_cache.get("macro_indicators")
    if cached_macro:
        return cached_macro

    import requests
    try:
        # Use environment variable for proxy URL if available
        macro_proxy_url = os.getenv("MACRO_PROXY_URL", "https://sync-compare-charts.onrender.com/api/macro")
        resp = requests.get(macro_proxy_url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            
            indicators = []
            if "results" in data:
                for item in data["results"]:
                    impact = "neutral"
                    if item["symbol"] in ["T10Y2Y", "T10Y3M"]:
                        impact = "negative" if item["value"] < 0 else "positive"
                    elif item["symbol"] in ["BAMLH0A0HYM2", "^VIX"]:
                        impact = "negative" if item["value"] > 20 else ("neutral" if item["value"] > 4 else "positive")
                        
                    indicators.append({
                        "id": item["symbol"],
                        "name": item["name"],
                        "value": round(item["value"], 2),
                        "impact": impact,
                        "trend": "up" if item["change"] > 0 else ("down" if item["change"] < 0 else "flat"),
                        "desc": item["desc"],
                        "link": item.get("link", "#"),
                        "history": [{"date": c["time"], "value": c["value"]} for c in item.get("chart_data", [])]
                    })
                    
            if "net_liquidity" in data:
                nl = data["net_liquidity"]
                indicators.append({
                    "id": nl["symbol"],
                    "name": nl["name"],
                    "value": round(nl["value"], 2),
                    "impact": "positive" if nl["change"] > 0 else "negative",
                    "trend": "up" if nl["change"] > 0 else "down",
                    "desc": nl["desc"],
                    "link": nl.get("link", "#"),
                    "history": [{"date": c["time"], "value": c["value"]} for c in nl.get("chart_data", [])]
                })
                
            status = "stable"
            if "summary" in data and "level" in data["summary"]:
                if data["summary"]["level"] == "red": status = "risk"
                elif data["summary"]["level"] == "yellow": status = "warning"
                elif data["summary"]["level"] == "green": status = "stable"
                
            ai_summary = [data["summary"].get("text", "요약 정보를 불러올 수 없습니다.")]

            result = {
                "status": status,
                "indicators": indicators,
                "ai_summary": ai_summary
            }
            macro_cache.set("macro_indicators", result)
            return result
            
    except Exception as e:
        logger.error(f"Macro fetch error: {e}")
        
    return {
        "status": "warning",
        "indicators": FALLBACK_DATA,
        "ai_summary": ["데이터를 실시간으로 불러오는 중 오류가 발생했습니다. 임시 데이터를 표시합니다."]
    }

@app.post("/api/analyze/analyst")
async def get_multi_analyst_report(payload: Dict[str, Any] = Body(...)):
    """Generates detailed AI Analyst reports for multiple symbols."""
    symbols = payload.get("symbols", [])
    if not symbols:
        raise HTTPException(status_code=400, detail="No symbols provided")
        
    analyses = []
    end = datetime.now()
    start = end - timedelta(days=730)
    
    for asset in symbols:
        sym = asset.get('symbol')
        asset_type = asset.get('type')
        
        cache_key = f"analyst_{sym}"
        cached_report = analyze_cache.get(cache_key)
        if cached_report:
            analyses.append(cached_report)
            continue

        try:
            if asset_type == 'stock':
                df = get_stock_data(sym, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
                fund_data = get_valuation_metrics(sym)
            else:
                df = get_crypto_data(sym)
                fund_data = {"error": "Crypto assets do not have traditional fundamentals"}
                
            if df is not None and not df.empty:
                df_with_indicators = apply_indicators(df.copy())
                latest_tech = df_with_indicators.iloc[-1].fillna(0).to_dict()
                
                if 'Date' in latest_tech and isinstance(latest_tech['Date'], pd.Timestamp):
                    latest_tech['Date'] = latest_tech['Date'].strftime('%Y-%m-%d')
                    
                company_name = getattr(fund_data, "get", lambda x,y: sym)('longName', sym) if isinstance(fund_data, dict) else sym
                report = generate_analyst_report(sym, company_name, latest_tech, fund_data)
                
                analyze_cache.set(cache_key, report)
                analyses.append(report)
            else:
                analyses.append({"symbol": sym, "signal": "Hold", "summary": "데이터 부족"})
        except Exception as e:
            logger.error(f"Error generating analyst report for {sym}: {e}")
            analyses.append({"symbol": sym, "signal": "Hold", "summary": "분석 오류"})
            
    return {"analyses": analyses}

@app.post("/api/chat")
async def chat_with_ai(payload: Dict[str, Any] = Body(...)):
    """Handles conversational questions regarding the selected assets using Gemini."""
    symbols = payload.get("symbols", [])
    question = payload.get("question", "")
    
    if not symbols or not question:
         raise HTTPException(status_code=400, detail="Missing symbols or question")
         
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "EXAMPLEKEY" in api_key:
        return {"answer": "API 키가 설정되지 않았습니다."}
        
    import google.generativeai as genai
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash") # Fixed model name
    client = genai.Client(api_key=api_key)
    
    asset_names = ", ".join([s['symbol'] for s in symbols])
    prompt = f"투자전문가로서 사용자의 질문에 답변합니다. 현재 관심 자산: {asset_names}. 질문: {question}. 답변은 한국어로 3문단 이내로 명확하게 작성하세요."
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        return {"answer": response.text}
    except Exception as e:
        logger.error(f"Chat API Error: {e}")
        return {"answer": "AI 응답 생성 중 오류가 발생했습니다."}

@app.get("/api/trending")
async def get_trending_assets():
    """Returns trending assets."""
    try:
        import json
        filepath = os.path.join(os.path.dirname(__file__), "popular_assets.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {"assets": data}
        return {"assets": []}
    except Exception as e:
        logger.error(f"Trending assets load error: {e}")
        raise HTTPException(status_code=500, detail="Failed to load trending assets")

