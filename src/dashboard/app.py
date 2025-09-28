import streamlit as st
import plotly.express as px
import pandas as pd
import requests
import time
import json
import os
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# ================== VADER LEXICON DOWNLOAD ==================
nltk.download('vader_lexicon', quiet=True)

# ================== CONFIG ==================
# Load API keys: First from environment variables, fallback to config.json
if os.path.exists('config/config.json'):
    with open('config/config.json', 'r') as f:
        CONFIG = json.load(f)
else:
    CONFIG = {}

NEWS_API_KEY = os.getenv("NEWS_API_KEY", CONFIG.get('news_api_key', ''))
TWELVE_DATA_API_KEY = os.getenv("TWELVE_DATA_API_KEY", CONFIG.get('twelve_data_api_key', ''))
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY", CONFIG.get('alpha_vantage_api_key', ''))

# API URLs
COINGECKO_API_URL = "https://api.coingecko.com/api/v3"
TWELVE_DATA_URL = "https://api.twelvedata.com"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
NEWS_API_URL = "https://newsapi.org/v2/everything"

# ================== FUNCTIONS ==================
def get_crypto_price(symbol):
    try:
        url = f"{COINGECKO_API_URL}/simple/price?ids={symbol}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        return response.json().get(symbol, {}).get('usd', 0)
    except:
        return 0

def get_crypto_historical(symbol, days=5):
    try:
        url = f"{COINGECKO_API_URL}/coins/{symbol}/market_chart?vs_currency=usd&days={days}"
        response = requests.get(url, timeout=10)
        prices = response.json()['prices']
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except:
        return pd.DataFrame()

def get_stock_price(symbol):
    twelve_symbol = symbol.replace('.NS', ':NSE')
    av_symbol = symbol.replace('.NS', '.BSE')
    try:
        url = f"{TWELVE_DATA_URL}/quote?symbol={twelve_symbol}&apikey={TWELVE_DATA_API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if 'close' in data:
            return float(data['close'])
    except:
        pass
    try:
        url = f"{ALPHA_VANTAGE_URL}?function=GLOBAL_QUOTE&symbol={av_symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        if 'Global Quote' in data:
            return float(data['Global Quote']['05. price'])
    except:
        return 0
    return 0

def get_stock_historical(symbol, days=5):
    twelve_symbol = symbol.replace('.NS', ':NSE')
    try:
        url = f"{TWELVE_DATA_URL}/time_series?symbol={twelve_symbol}&interval=1day&outputsize={days}&apikey={TWELVE_DATA_API_KEY}"
        response = requests.get(url, timeout=10)
        data = response.json()
        values = data['values']
        df = pd.DataFrame(values)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['close'] = df['close'].astype(float)
        return df[['datetime', 'close']].rename(columns={'datetime': 'timestamp', 'close': 'price'})
    except:
        return pd.DataFrame()

def get_news_articles(symbol, count=10):
    base_query = symbol.replace('-USD', '').replace('.NS', '').replace(':NSE', '').replace('.BSE', '')
    if base_query.lower() in ['bitcoin', 'btc']:
        query = f"{base_query} OR BTC finance"
    else:
        query = f"{base_query} stock OR finance"
    params = {'q': query, 'apiKey': NEWS_API_KEY, 'language': 'en', 'sortBy': 'publishedAt', 'pageSize': count}
    try:
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        articles = response.json().get('articles', [])
        return [article['title'] + " " + (article['description'] or "") for article in articles]
    except:
        return []

def get_sentiment(texts):
    analyzer = SentimentIntensityAnalyzer()
    scores = []
    breakdown = []
    for text in texts:
        score = analyzer.polarity_scores(text)['compound']
        scores.append(score)
        breakdown.append("Positive" if score > 0.05 else "Negative" if score < -0.05 else "Neutral")
    avg_score = sum(scores) / len(scores) if scores else 0
    return {'avg': avg_score, 'breakdown': breakdown}

# ================== STYLING ==================
st.set_page_config(page_title="Sentiment Dashboard 🚀", page_icon="📈", layout="wide")

st.markdown("""
    <style>
        .stApp { background: linear-gradient(to right, #141e30, #243b55); color: white; }
        h1, h2, h3, h4 { color: #f8f9fa !important; text-align: center; }
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem !important; }
            h2 { font-size: 1.4rem !important; }
            .stMetric { font-size: 0.9rem; }
            .news-box { font-size: 0.85rem; }
        }
        .stMetric { background: #1e293b; padding: 15px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.4); text-align: center; }
        .news-box { background: #1f2937; padding: 12px; margin: 6px 0; border-radius: 10px; color: #f1f5f9; }
        .js-plotly-plot { width: 100% !important; height: auto !important; }
        .footer { text-align: center; padding: 15px; font-size: 0.9rem; color: #cbd5e1; margin-top: 40px; }
    </style>
""", unsafe_allow_html=True)

# ================== DASHBOARD ==================
st.title("📊 Cool Crypto & Stock Sentiment Dashboard")

assets = {
    "Bitcoin (BTC)": {"id": "bitcoin", "type": "crypto"},
    "Ethereum (ETH)": {"id": "ethereum", "type": "crypto"},
    "Reliance (RELIANCE.NS)": {"id": "RELIANCE.NS", "type": "stock"},
    "Tata Steel (TATASTEEL.NS)": {"id": "TATASTEEL.NS", "type": "stock"}
}
selected_asset = st.sidebar.selectbox("🔎 Select Asset", list(assets.keys()))
asset_id = assets[selected_asset]["id"]
asset_type = assets[selected_asset]["type"]

if st.sidebar.button("⚡ Update Live Data"):
    with st.spinner("Fetching data..."):
        price = get_crypto_price(asset_id) if asset_type == "crypto" else get_stock_price(asset_id)
        news_texts = get_news_articles(asset_id)
        sentiment_data = get_sentiment(news_texts)

        col1, col2, col3 = st.columns(3)
        col1.metric("💰 Current Price", f"${price:.2f}" if price > 0 else "N/A")
        col2.metric("📰 News Articles", len(news_texts))
        col3.metric("😊 Sentiment Score", f"{sentiment_data['avg']:.2f}", delta=sentiment_data['avg'] * 100)

        if news_texts:
            st.subheader("📰 Latest News Headlines")
            for i, text in enumerate(news_texts[:5]):
                st.markdown(f"<div class='news-box'><b>{i+1}.</b> {text}</div>", unsafe_allow_html=True)

        # Historical Data
        df = get_crypto_historical(asset_id) if asset_type == "crypto" else get_stock_historical(asset_id)
        if not df.empty:
            fig = px.line(df, x='timestamp', y='price',
                          title=f"{selected_asset} Price (Last 5 Days)",
                          template="plotly_dark")
            st.plotly_chart(fig, use_container_width=True)

        # Sentiment Pie
        if news_texts:
            df_sent = pd.DataFrame({'Sentiment': sentiment_data['breakdown']})
            fig_pie = px.pie(df_sent, names='Sentiment',
                             title="News Sentiment Distribution",
                             hole=0.4, template="plotly_dark",
                             color_discrete_sequence=px.colors.sequential.RdBu)
            st.plotly_chart(fig_pie, use_container_width=True)

        st.success("✅ Data updated successfully!")

# Footer
st.markdown("<div class='footer'>Made with ❤️ by Sanu</div>", unsafe_allow_html=True)

# ================== AUTO REFRESH ==================
if st.sidebar.checkbox("🔄 Auto-Refresh (60s)"):
    time.sleep(60)
    st.rerun()
