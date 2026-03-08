import os
import json
import re
from google import genai

def generate_investment_report(symbol: str, latest_metrics: dict, backtest_results: dict) -> dict:
    """Uses Gemini 2.5 Flash to generate an investment opinion based on data."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "EXAMPLEKEY" in api_key:
        return {
            "buy_reason": "API Key is missing or invalid. Set GOOGLE_API_KEY in .env.",
            "sell_reason": "API Key is missing.",
            "overall_opinion": "Hold"
        }
        
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert financial analyst. Analyze the following data for {symbol}.
    
    Latest Technical Indicators (Daily):
    {latest_metrics}
    
    5-Year Backtest Results (Strategy: SMA 20/50 Golden Cross + RSI):
    {backtest_results}
    
    Based on this data, provide a professional, emotionless, data-driven report.
    Format your response EXACTLY as a JSON object with these three keys:
    1. "buy_reason": A 2-sentence explanation of why one might BUY {symbol} now.
    2. "sell_reason": A 2-sentence explanation of why one might SELL {symbol} now.
    3. "overall_opinion": Choose one of: "Strong Buy", "Buy", "Hold", "Sell", "Strong Sell".
    """
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        
        text = response.text
        # Remove markdown ticks to extract pure JSON
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {
            "error": "Could not parse AI response", 
            "raw": text,
            "overall_opinion": "Hold"
        }
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return {
            "buy_reason": "Error generating insight from Gemini API.",
            "sell_reason": "Error generating insight from Gemini API.",
            "overall_opinion": "Hold"
        }

def summarize_global_news(news_data: dict) -> dict:
    """Uses Gemini 2.5 Flash to summarize the global news into a 3-line Threads format."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "EXAMPLEKEY" in api_key:
        return {
            "summary_points": [
                "API 키가 누락되어 뉴스 요약을 가져올 수 없습니다.",
                "1. .env 파일에 GOOGLE_API_KEY를 추가하세요.",
                "2. 그리고 백엔드 서버를 다시 시작하세요."
            ]
        }
        
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert financial writer. Please read the following news headlines and descriptions from the stock market and crypto market today.
    
    News Data:
    {json.dumps(news_data, indent=2, ensure_ascii=False)}
    
    Write a highly engaging, emotionless but professional 3-bullet-point summary of the global markets right now for a "Threads" post.
    Format your response EXACTLY as a JSON object with this key:
    {{
      "summary_points": [
        "First point about macro/stocks...",
        "Second point about crypto...",
        "Third point highlighting a specific trend or warning..."
      ]
    }}
    Please write the content in Korean.
    """
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        text = response.text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return {
            "summary_points": ["Could not parse AI response", text]
        }
        except Exception as e:
        print(f"News Summarization Error: {e}")
        return {
            "summary_points": ["Error requesting news summary from Gemini API."]
        }

def generate_analyst_report(symbol: str, company_name: str, tech_data: dict, fund_data: dict) -> dict:
    """Uses Gemini 2.5 Flash to act as an AI Analyst and return a structured report."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "EXAMPLEKEY" in api_key:
        return {
            "symbol": symbol,
            "company_name": company_name,
            "signal": "Hold",
            "technical_analysis": "API 에러: GOOGLE_API_KEY가 없습니다.",
            "fundamental_analysis": "API 에러: GOOGLE_API_KEY가 없습니다.",
            "summary": "API 연동 실패"
        }
        
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")
    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an elite Wall Street AI Analyst. Please perform a multi-perspective analysis on the following asset.
    Asset: {company_name} ({symbol})
    
    Technical Data (Moving Averages, RSI, MACD, etc.):
    {tech_data}
    
    Fundamental Data (P/E, P/B, Market Cap, Growth, etc.):
    {fund_data}
    
    Based on the provided data, generate a comprehensive evaluation. 
    Format your response EXACTLY as a JSON object with the following keys. Please write the content in highly professional Korean.
    {{
      "symbol": "{symbol}",
      "company_name": "{company_name}",
      "signal": "Choose exactly one: Strong Buy, Buy, Hold, Sell, Strong Sell",
      "technical_analysis": "A concise 3-4 sentence paragraph summarizing technical trends (e.g. golden cross, RSI momentum). You may use markdown.",
      "fundamental_analysis": "A concise 3-4 sentence paragraph summarizing fundamental valuation (e.g. undervalued, growth potential). You may use markdown.",
      "summary": "A powerful 1-line final verdict summarizing your stance."
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        text = response.text
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
             return json.loads(match.group(0))
        return {
            "symbol": symbol,
            "company_name": company_name,
            "signal": "Hold",
            "technical_analysis": "데이터 분석 실패",
            "fundamental_analysis": "데이터 분석 실패",
            "summary": "알 수 없음"
        }
    except Exception as e:
        print(f"Analyst Report Error for {symbol}: {e}")
        return {
             "symbol": symbol,
             "company_name": company_name,
             "signal": "Hold",
             "technical_analysis": f"API 호출 중 오류가 발생했습니다: {str(e)}",
             "fundamental_analysis": "오류 발생",
             "summary": "분석 실패"
        }
