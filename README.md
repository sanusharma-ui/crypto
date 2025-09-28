Crypto/Stock Sentiment Dashboard
A real-time dashboard for crypto (CoinGecko) and stock (Twelve Data, NSE support) prices with news sentiment analysis (NewsAPI, VADER).
Setup

Clone repo and create virtual environment:
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate (Windows)


Install dependencies:
pip install -r requirements.txt


Add API keys to config/config.json:

Twelve Data: twelvedata.com
NewsAPI: newsapi.org
Alpha Vantage: alphavantage.co


Run dashboard:
streamlit run src/dashboard/app.py



Features

Real-time prices (BTC, ETH, RELIANCE.NS, TATASTEEL.NS)
News-based sentiment analysis
Price and sentiment charts
Auto-refresh every 60s

Notes

CoinGecko: ~30 calls/min, no key needed.
Twelve Data: Free tier, NSE support.
NewsAPI: 100 calls/day (free).
