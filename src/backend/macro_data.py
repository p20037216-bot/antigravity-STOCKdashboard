import os
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from fredapi import Fred
import concurrent.futures

# Configure indicators mapping
INDICATORS = {
    "10y_2y": {"id": "T10Y2Y", "name": "장단기 금리차 (10y-2y)", "desc": "10년물과 2년물 국채 금리 차이. 음수(-)일 경우 경기 침체 전조 현상으로 해석됩니다."},
    "10y_3m": {"id": "T10Y3M", "name": "장단기 금리차 (10y-3m)", "desc": "연준이 가장 신뢰하는 침체 지표. 10년물과 3개월물 금리 차이입니다."},
    "high_yield": {"id": "BAMLH0A0HYM2", "name": "하이일드 스프레드", "desc": "위험 기업과 안전 국가의 채권 금리 차이. 높을수록 기업 부도 위험이 커집니다."},
    "rrp": {"id": "RRPONTSYD", "name": "역레포 잔액 (B)", "desc": "시장의 잉여 유동성을 빨아들이는 지표. 잔액이 줄어들면 주식시장에 호재입니다."},
    "real_rate": {"id": "DFII10", "name": "10년 실질금리", "desc": "명목금리에서 물가상승률을 뺀 진짜 금리. 높으면 기술주와 성장에 부담을 줍니다."},
    "breakeven": {"id": "T10YIE", "name": "기대 인플레이션", "desc": "시장이 예상하는 향후 10년 평균 물가상승률입니다. 2% 부근이 이상적입니다."},
    "unemployment": {"id": "UNRATE", "name": "실업률 (%)", "desc": "노동 시장의 건강 상태. 급격히 상승하면 경기 침체(Sahm Rule)가 우려됩니다."},
    "retail": {"id": "RSAFS", "name": "소매판매 (M)", "desc": "미국 경제의 70%를 차지하는 소비 지표. 견조할수록 경제 골디락스에 유리합니다."},
    "fed_assets": {"id": "WALCL", "name": "연준 총자산 (M)", "desc": "연준이 푼 돈의 양(양적완화/긴축). 자산이 늘어나면 주식시장에 매우 긍정적입니다."},
    "tga": {"id": "WTREGEN", "name": "미 재무부 일반계정 (B)", "desc": "미국 정부의 통장 잔고. 이 돈이 줄어들면(정부가 돈을 쓰면) 시중 유동성이 늘어납니다."},
    "m2": {"id": "WM2NS", "name": "M2 통화량 (B)", "desc": "시중에 풀린 돈의 총량입니다. 지속적으로 우상향하는 것이 위험 자산에 유리합니다."},
    "fed_funds": {"id": "DFF", "name": "연방기금금리", "desc": "미국 기준금리. 금리 인하 사이클이 시작되면 일반적으로 시장에 유동성이 공급됩니다."},
}

# Pre-defined mock data in case FRED API key is missing or fails
MOCK_DATA = [
    {"id": "10y_2y", "name": "장단기 금리차 (10y-2y)", "value": -0.32, "impact": "negative", "trend": "down", "desc": "10년물과 2년물 국채 금리 차이. 음수(-)일 경우 경기 침체 전조 현상으로 해석됩니다.", "history": [{"date": "2024-01-01", "value": -0.5}, {"date": "2024-03-01", "value": -0.32}]},
    {"id": "high_yield", "name": "하이일드 스프레드", "value": 3.42, "impact": "positive", "trend": "flat", "desc": "위험 기업과 안전 국가의 채권 금리 차이. 높을수록 기업 부도 위험이 커집니다.", "history": [{"date": "2024-01-01", "value": 4.0}, {"date": "2024-03-01", "value": 3.42}]},
    {"id": "vix", "name": "공포지수 (VIX)", "value": 14.2, "impact": "positive", "trend": "down", "desc": "S&P500의 향후 30일 변동성 기대치. 20 이하면 안정, 30 이상이면 패닉 장세입니다.", "history": [{"date": "2024-01-01", "value": 16.0}, {"date": "2024-03-01", "value": 14.2}]},
]

def determine_impact(key, current_val, prev_val):
    """Determine if the current state is positive, negative, or neutral for the stock market."""
    if pd.isna(current_val):
        return "neutral"
        
    diff = current_val - prev_val
    
    # 1. Yield Spreads (Negative is bad)
    if key in ["10y_2y", "10y_3m"]:
        if current_val < 0: return "negative" # Inverted curve
        if current_val > 0.5: return "positive" # Healthy curve
        return "neutral"
        
    # 2. High Yield Spread (High is bad)
    if key == "high_yield":
        if current_val > 5.0: return "negative" # High stress
        if current_val < 4.0: return "positive" # Risk-on behavior
        return "neutral"
        
    # 3. RRP, TGA, Real Rate (High is bad for liquidity/tech)
    if key in ["rrp", "tga", "real_rate", "fed_funds"]:
        if diff > 0: return "negative" # Liquidity draining / rates rising
        if diff < 0: return "positive" # Liquidity injecting / rates falling
        return "neutral"
        
    # 4. Breakeven Inflation
    if key == "breakeven":
        if current_val > 2.5: return "negative" # Inflation running hot
        if current_val < 1.0: return "negative" # Deflation fears
        return "positive" # Goldilocks target ~2%
        
    # 5. Unemployment
    if key == "unemployment":
        if current_val > 4.5 or diff > 0.2: return "negative" # Sahm rule trigger
        return "positive"
        
    # 6. Retail & M2 & Fed Assets (Rising is generally good)
    if key in ["retail", "m2", "fed_assets"]:
        if diff > 0: return "positive"
        if diff < 0: return "negative"
        return "neutral"
        
    # 7. VIX
    if key == "vix":
        if current_val > 25: return "negative"
        if current_val < 18: return "positive"
        return "neutral"
        
    return "neutral"

def fetch_single_fred_indicator(fred, key, info, start_date):
    """Fetch a single dataseries from FRED"""
    try:
        series = fred.get_series(info["id"], observation_start=start_date)
        if series.empty:
            return None
            
        # Resample to weekly to reduce frontend payload (keep last 6 months manageable)
        series = series.resample('W-FRI').last().dropna()
        
        current_val = float(series.iloc[-1])
        prev_val = float(series.iloc[0]) if len(series) > 1 else current_val
        
        # Format history for frontend
        history = [{"date": idx.strftime('%Y-%m-%d'), "value": float(val)} for idx, val in series.items()]
        
        # Scaling modifications for readability
        if key == "rrp":
            current_val = current_val # FRED RRP is already in Billions
        elif key == "fed_assets":
            current_val = current_val / 1000 # Convert to Trillions visually sometimes, but keep M
            
        impact = determine_impact(key, current_val, prev_val)
        trend = "up" if current_val > prev_val else ("down" if current_val < prev_val else "flat")
        
        return {
            "id": key,
            "name": info["name"],
            "value": round(current_val, 2),
            "impact": impact,
            "trend": trend,
            "desc": info["desc"],
            "history": history
        }
    except Exception as e:
        print(f"Failed fetching FRED data for {key}: {e}")
        return None

def fetch_vix(start_date):
    """Fetch VIX from yfinance"""
    try:
        vix = yf.download('^VIX', start=start_date, progress=False)
        if vix.empty:
            return None
            
        # Handle multi-index columns from new yfinance versions
        if isinstance(vix.columns, pd.MultiIndex):
            vix = vix['Close']['^VIX']
        else:
            vix = vix['Close']
            
        vix = vix.resample('W-FRI').last().dropna()
        current_val = float(vix.iloc[-1])
        prev_val = float(vix.iloc[0]) if len(vix) > 1 else current_val
        history = [{"date": idx.strftime('%Y-%m-%d'), "value": float(val)} for idx, val in vix.items()]
        
        impact = determine_impact("vix", current_val, prev_val)
        trend = "up" if current_val > prev_val else ("down" if current_val < prev_val else "flat")
        
        return {
            "id": "vix",
            "name": "공포지수 (VIX)",
            "value": round(current_val, 2),
            "impact": impact,
            "trend": trend,
            "desc": "S&P500의 향후 30일 변동성 기대치. 20 이하면 안정, 30 이상이면 패닉 장세입니다.",
            "history": history
        }
    except Exception as e:
        print(f"Failed fetching VIX data: {e}")
        return None

async def get_all_macro_data():
    """Asynchronously fetch all 13 macro indicators"""
    fred_key = os.getenv("FRED_API_KEY")
    
    # If no valid FRED key, return mock data immediately to prevent crashes
    if not fred_key or fred_key == "EXAMPLE_FRED_API_KEY_HERE":
        return MOCK_DATA
        
    try:
        fred = Fred(api_key=fred_key)
    except Exception as e:
        print(f"FRED Auth failed: {e}")
        return MOCK_DATA
        
    # Last 6 months
    start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    
    results = []
    
    # Fetch in parallel using ThreadPoolExecutor for speed
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # Submit FRED tasks
        future_to_key = {
            executor.submit(fetch_single_fred_indicator, fred, key, info, start_date): key 
            for key, info in INDICATORS.items()
        }
        # Submit VIX task
        future_vix = executor.submit(fetch_vix, start_date)
        
        for future in concurrent.futures.as_completed(future_to_key):
            res = future.result()
            if res:
                results.append(res)
                
        # Get VIX
        vix_res = future_vix.result()
        if vix_res:
            results.append(vix_res)
            
    # If API rate limits hit and nothing returned, fallback to mock
    if len(results) == 0:
        return MOCK_DATA
        
    return results
