import requests
import json

with open('config/config.json', 'r') as f:
    CONFIG = json.load(f)

NEWS_API_KEY = CONFIG['news_api_key']
NEWS_API_URL = "https://newsapi.org/v2/everything"

def get_news_articles(symbol, count=10):
    """
    Fetch news articles (optimized query).
    """
    # Better query: Add OR for symbols
    base_query = symbol.replace('-USD', '').replace('.NS', '').replace(':NSE', '').replace('.BSE', '')
    if base_query.lower() in ['bitcoin', 'btc']:
        query = f"{base_query} OR BTC finance"
    else:
        query = f"{base_query} stock OR finance"
    params = {
        'q': query,
        'apiKey': NEWS_API_KEY,
        'language': 'en',
        'sortBy': 'publishedAt',
        'pageSize': count
    }
    try:
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"NewsAPI Response for '{query}': {len(data.get('articles', []))} articles")  # Debug
        articles = data.get('articles', [])
        return [article['title'] + " " + (article['description'] or "") for article in articles]
    except requests.RequestException as e:
        print(f"Error fetching news for {symbol}: {e}")
        return []