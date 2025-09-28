import requests
import pandas as pd
import json

with open('config/config.json', 'r') as f:
    CONFIG = json.load(f)

TWELVE_DATA_API_KEY = CONFIG['twelve_data_api_key']
ALPHA_VANTAGE_API_KEY = CONFIG['alpha_vantage_api_key']
TWELVE_DATA_URL = "https://api.twelvedata.com"
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"

def get_stock_price(symbol):
    """
    Fetch latest stock price using Twelve Data (NSE format: SYMBOL:NSE). Fallback to Alpha Vantage (RELIANCE.BSE).
    """
    # Fix for NSE: Use :NSE for Twelve Data, .BSE for Alpha Vantage
    twelve_symbol = symbol.replace('.NS', ':NSE')  # e.g., RELIANCE.NS -> RELIANCE:NSE
    av_symbol = symbol.replace('.NS', '.BSE')      # e.g., RELIANCE.NS -> RELIANCE.BSE
    
    try:
        # Twelve Data first
        url = f"{TWELVE_DATA_URL}/quote?symbol={twelve_symbol}&apikey={TWELVE_DATA_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"Twelve Data Response for {twelve_symbol}: {data}")  # Debug
        if 'close' in data:
            return float(data['close'])
    except requests.RequestException as e:
        print(f"Twelve Data error for {symbol}: {e}")
        # Fallback to Alpha Vantage
        try:
            url = f"{ALPHA_VANTAGE_URL}?function=GLOBAL_QUOTE&symbol={av_symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            print(f"Alpha Vantage Response for {av_symbol}: {data}")  # Debug
            if 'Global Quote' in data and '05. price' in data['Global Quote']:
                return float(data['Global Quote']['05. price'])
        except (requests.RequestException, KeyError) as e:
            print(f"Alpha Vantage error for {symbol}: {e}")
            return 0
    return 0

def get_stock_historical(symbol, days=5):
    """
    Fetch historical stock data (fixed symbol format).
    """
    twelve_symbol = symbol.replace('.NS', ':NSE')
    try:
        url = f"{TWELVE_DATA_URL}/time_series?symbol={twelve_symbol}&interval=1day&outputsize={days}&apikey={TWELVE_DATA_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        print(f"Twelve Historical for {twelve_symbol}: {len(data.get('values', []))} records")  # Debug
        values = data['values']
        df = pd.DataFrame(values)
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['close'] = df['close'].astype(float)
        return df[['datetime', 'close']].rename(columns={'datetime': 'timestamp', 'close': 'price'})
    except requests.RequestException as e:
        print(f"Error fetching {symbol} historical data: {e}")
        return pd.DataFrame()