import requests
import pandas as pd

COINGECKO_API_URL = "https://api.coingecko.com/api/v3"

def get_crypto_price(symbol):
    """
    Fetch latest price for a cryptocurrency (e.g., 'bitcoin', 'ethereum') using CoinGecko.
    """
    try:
        url = f"{COINGECKO_API_URL}/simple/price?ids={symbol}&vs_currencies=usd"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get(symbol, {}).get('usd', 0)
    except requests.RequestException as e:
        print(f"Error fetching {symbol} price: {e}")
        return 0

def get_crypto_historical(symbol, days=5):
    """
    Fetch historical price data for charting.
    """
    try:
        url = f"{COINGECKO_API_URL}/coins/{symbol}/market_chart?vs_currency=usd&days={days}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        prices = data['prices']  # [[timestamp, price], ...]
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        return df
    except requests.RequestException as e:
        print(f"Error fetching {symbol} historical data: {e}")
        return pd.DataFrame()