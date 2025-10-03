# pricefetcher.py

import requests


def get_price(symbol="BNB"):
    try:
        pair = f"{symbol.upper()}USDT"
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={pair}"
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            print(f"⚠️ Binance API error for {pair}")
            return None
        return float(response.json()["price"])
    except Exception as e:
        print(f"⚠️ Failed to fetch {symbol} price: {e}")
        return None
