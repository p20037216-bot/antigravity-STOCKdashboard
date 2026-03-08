from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from .data_collector import get_stock_data, get_crypto_data, get_valuation_metrics
from .indicators import apply_indicators
from .backtester import run_backtest
from .ai_reporter import generate_investment_report, summarize_global_news
from .news_crawler import get_global_news
from .macro_data import get_all_macro_data
import pandas as pd
from datetime import datetime, timedelta
import dotenv
import math
import os

# Load environment variables
dotenv.load_dotenv()

app = FastAPI(title="Antigravity Finance Dashboard API")

app.add_middleware(
    CORSMiddleware,
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
    try:
        # 1. Collect Data
        if asset_type.lower() == "stock":
            end = datetime.now()
            start = end - timedelta(days=1825)
            df = get_stock_data(symbol, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))
        elif asset_type.lower() == "crypto":
            # CCXT expects something like "ETH/USDT"
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
        # Replace NaN with 0 to prevent JSON serialization errors
        df_clean = df_with_indicators.fillna(0)
        
        # Fix infiniti/NaN numbers natively so json encoder doesnt crash
        for col in df_clean.select_dtypes(include=['float']).columns:
            df_clean[col] = df_clean[col].apply(lambda x: 0.0 if math.isnan(x) or math.isinf(x) else x)

        latest_data = df_clean.iloc[-1].to_dict()
        
        # Prevent "Date" type serialization error if Date is an index
        if 'Date' in latest_data and isinstance(latest_data['Date'], pd.Timestamp):
            latest_data['Date'] = latest_data['Date'].strftime('%Y-%m-%d')
            
        ai_report = generate_investment_report(symbol, latest_data, backtest_results)
        
        # Only return the last 100 days of data for the frontend chart to remain lightweight
        chart_data = df_clean.tail(100).reset_index()
        # Ensure datetime is serializable
        if 'Date' in chart_data.columns:
            chart_data['Date'] = chart_data['Date'].dt.strftime('%Y-%m-%d')
            
        records = chart_data.to_dict(orient='records')
        
        return {
            "symbol": symbol,
            "type": asset_type,
            "backtest_metrics": backtest_results,
            "ai_analysis": ai_report,
            "chart_data": records
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/news")
async def get_news_summary():
    """Fetches latest news and returns an AI summary."""
    try:
        news_data = get_global_news()
        ai_summary = summarize_global_news(news_data)
        return {
            "raw_news": news_data,
            "ai_summary": ai_summary
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/overview")
async def get_market_overview():
    """Gets a quick overview of predefined major assets (Stocks + Crypto) without AI generation to speed up load time."""
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
                df = get_crypto_data(f'{asset["symbol"]}/USDT')
                
            if df is not None and not df.empty:
                df_with_indicators = apply_indicators(df.copy())
                backtest_results = run_backtest(df.copy())
                
                # Derive a quick signal based on MA crossing and RSI
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
            print(f"Skipping {asset['symbol']} due to error: {e}")
            
    return {"overview": results}

@app.post("/api/compare/chart")
async def compare_charts(payload: Dict[str, Any] = Body(...)):
    """Accepts a list of symbols and a timeframe, returning synchronized percentage returns."""
    symbols = payload.get("symbols", [])
    
    # Handle custom dates or fallback to 3 years
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
                df = get_crypto_data(f'{sym}/USDT')
                # Crypto data might be longer, slice to timeframe
                df = df[df.index >= start]
            
            if df is not None and not df.empty:
                # Calculate percentage return from the first valid close price in the window
                base_price = df['close'].iloc[0]
                df['pct_return'] = ((df['close'] - base_price) / base_price) * 100
                
                # Convert to dict format with string dates for JSON
                for date, row in df.iterrows():
                    date_str = date.strftime('%Y-%m-%d')
                    if date_str not in combined_data:
                        combined_data[date_str] = {"date": date_str}
                    
                    combined_data[date_str][sym] = 0.0 if math.isnan(row['pct_return']) else float(row['pct_return'])
        except Exception as e:
            print(f"Error processing {sym} for chart compare: {e}")
            
    # Sort the dictionary by date and return as a flat list
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
    """Fetches key macroeconomic indicators using FRED API and YFinance."""
    indicators = await get_all_macro_data()
    
    # Calculate overall traffic light status (how many negative signals?)
    negative_count = sum(1 for item in indicators if item.get("impact") == "negative")
    
    status = "stable"
    if negative_count >= 5:
        status = "risk"
    elif negative_count >= 2:
        status = "warning"
        
    ai_summary = [
        "13개의 거시경제 지표 데이터를 바탕으로 분석한 기본 코멘트입니다.",
        "현재 전체 지표 중 부정적 신호를 보내는 지표 개수를 주시하세요."
    ]
        
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key and "EXAMPLEKEY" not in api_key:
        try:
            import google.generativeai as genai
            model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
            client = genai.Client(api_key=api_key)
            prompt = f"투자전문가로서 거시경제 지표 요약을 보고 시장을 3개의 불릿포인트 문장으로(각각 짧게) 요약해주세요. 위험지표 갯수: {negative_count}개. 현재상태: {status}. 데이터일부: {indicators[:5]}"
            response = client.models.generate_content(model=model_name, contents=prompt)
            lines = [line.strip("- *").strip() for line in response.text.split("\n") if line.strip() and ("-" in line or "*" in line)]
            if lines:
                ai_summary = lines[:3]
            else:
                ai_summary = [response.text]
        except Exception as e:
            print(f"Macro AI Summary Error: {e}")
            
    return {
        "status": status,
        "indicators": indicators,
        "ai_summary": ai_summary
    }

@app.post("/api/chat")
async def chat_with_ai(payload: Dict[str, Any] = Body(...)):
    """Handles conversational questions regarding the selected assets using Gemini."""
    symbols = payload.get("symbols", [])
    question = payload.get("question", "")
    
    if not symbols or not question:
         raise HTTPException(status_code=400, detail="Missing symbols or question")
         
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "EXAMPLEKEY" in api_key:
        return {"answer": "Error: Google API Key is missing. Please add it to your .env file."}
        
    import google.generativeai as genai
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
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
        print(f"Chat API Error: {e}")
        return {"answer": "AI 응답을 생성하는 중 오류가 발생했습니다."}

@app.get("/api/trending")
async def get_trending_assets():
    """Returns the list of on-demand trending assets generated by the background crawler."""
    try:
        # Load from the JSON file created by the crawler
        import json
        import os
        filepath = os.path.join(os.path.dirname(__file__), "popular_assets.json")
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return {"assets": data}
        else:
            return {"assets": []}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to load trending assets")

