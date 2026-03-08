import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def fetch_rss_news(feed_url: str, max_items: int = 5) -> list:
    """Fetch and parse an RSS feed, returning a list of dictionaries with title, link, and summary."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)'
    }
    
    try:
        response = requests.get(feed_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse XML
        root = ET.fromstring(response.content)
        items = []
        
        # Usually RSS is enclosed in <channel> -> <item>
        for item in root.findall('.//item')[:max_items]:
            title = item.find('title').text if item.find('title') is not None else ''
            link = item.find('link').text if item.find('link') is not None else ''
            
            # Extract description text using BeautifulSoup to strip HTML tags
            desc_elem = item.find('description')
            description = ''
            if desc_elem is not None and desc_elem.text:
                soup = BeautifulSoup(desc_elem.text, 'html.parser')
                description = soup.get_text()[:200] + '...' # Truncate long descriptions
                
            pubDate = item.find('pubDate').text if item.find('pubDate') is not None else ''
            
            items.append({
                "title": title,
                "link": link,
                "description": description.strip(),
                "published_at": pubDate
            })
            
        return items
    except Exception as e:
        print(f"Error fetching RSS {feed_url}: {e}")
        return []

def get_global_news() -> dict:
    """Fetch news from multiple sources."""
    
    # Define RSS sources
    sources = {
        "stock_market": "https://finance.yahoo.com/news/rssindex",
        "crypto": "https://cointelegraph.com/rss"
    }
    
    news_data = {}
    for category, url in sources.items():
        news_data[category] = fetch_rss_news(url)
        
    return news_data
