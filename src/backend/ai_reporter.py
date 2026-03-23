import os
import json
import re
import logging
from google import genai

logger = logging.getLogger(__name__)

def extract_json(text: str) -> dict:
    """Robustly extract JSON from a string that might contain markdown or other text."""
    try:
        # First attempt: directly parse
        return json.loads(text)
    except json.JSONDecodeError:
        # Second attempt: look for JSON object using regex
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                # Third attempt: try to fix common AI JSON errors like trailing commas
                fixed_json = re.sub(r',\s*\}', '}', match.group(0))
                fixed_json = re.sub(r',\s*\]', ']', fixed_json)
                try:
                    return json.loads(fixed_json)
                except json.JSONDecodeError:
                    pass
    return None

def generate_investment_report(symbol: str, latest_metrics: dict, backtest_results: dict) -> dict:
    """Uses Gemini to generate an investment opinion based on data."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "EXAMPLEKEY" in api_key:
        return {
            "buy_reason": "API Key is missing. Please set GOOGLE_API_KEY.",
            "sell_reason": "API Key is missing.",
            "overall_opinion": "Hold"
        }
        
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
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
        
        result = extract_json(response.text)
        if result:
            return result
            
        logger.warning(f"Failed to parse AI response for {symbol}: {response.text[:100]}...")
        return {
            "buy_reason": "Analysis data received but could not be formatted.",
            "sell_reason": "Analysis data received but could not be formatted.",
            "overall_opinion": "Hold"
        }
    except Exception as e:
        logger.error(f"AI Generation Error for {symbol}: {e}")
        return {
            "buy_reason": "Error connecting to AI analysis service.",
            "sell_reason": "Error connecting to AI analysis service.",
            "overall_opinion": "Hold"
        }

def summarize_global_news(news_data: dict) -> dict:
    """Uses Gemini to summarize the global news into a 3-line format."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "EXAMPLEKEY" in api_key:
        return {
            "summary_points": ["API 키가 설정되지 않았습니다."]
        }
        
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert financial writer. Please read the following news headlines.
    
    News Data:
    {json.dumps(news_data, indent=2, ensure_ascii=False)}
    
    Write a professional 3-bullet-point summary of the global markets right now.
    Format your response EXACTLY as a JSON object with this key:
    {{
      "summary_points": [
        "Point 1...",
        "Point 2...",
        "Point 3..."
      ]
    }}
    Please write the content in Korean.
    """
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        result = extract_json(response.text)
        if result:
            return result
        return {"summary_points": ["뉴스 요약을 분석할 수 없습니다."]}
    except Exception as e:
        logger.error(f"News Summarization Error: {e}")
        return {"summary_points": ["뉴스 요약 생성 중 오류가 발생했습니다."]}

def generate_analyst_report(symbol: str, company_name: str, tech_data: dict, fund_data: dict) -> dict:
    """Uses Gemini to act as an AI Analyst and return a structured report."""
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key or "EXAMPLEKEY" in api_key:
        return {
            "symbol": symbol,
            "company_name": company_name,
            "signal": "Hold",
            "summary": "API 키 누락"
        }
        
    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an elite AI Financial Analyst. Analyze {company_name} ({symbol}).
    
    Technical: {tech_data}
    Fundamental: {fund_data}
    
    Return a JSON object:
    {{
      "symbol": "{symbol}",
      "company_name": "{company_name}",
      "signal": "Strong Buy/Buy/Hold/Sell/Strong Sell",
      "technical_analysis": "Concise summary in Korean",
      "fundamental_analysis": "Concise summary in Korean",
      "summary": "Final verdict in Korean"
    }}
    """
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt
        )
        result = extract_json(response.text)
        if result:
             return result
        return {"symbol": symbol, "signal": "Hold", "summary": "분석 결과 파싱 실패"}
    except Exception as e:
        logger.error(f"Analyst Report Error for {symbol}: {e}")
        return {"symbol": symbol, "signal": "Hold", "summary": "AI 분석 중 오류 발생"}
