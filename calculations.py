import requests


def get_live_price(coin_name):
    """
    Fetch live coin prices from CoinGecko API.
    Falls back to mock price if API fails.
    """
    coin_map = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "BNB": "binancecoin",
        "SOL": "solana",
        "ADA": "cardano",
        "XRP": "ripple",
    }

    coin_id = coin_map.get(coin_name.upper())
    if not coin_id:
        print(
            f"⚠️ No CoinGecko ID found for {coin_name}, using fallback mock price.")
        return 100.0

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        resp = requests.get(url, timeout=10)
        data = resp.json()
        return data[coin_id]["usd"]
    except Exception as e:
        print(f"⚠️ Could not fetch live price for {coin_name}: {e}")
        return 100.0


def calculate_trade(action, confidence, portfolio_value, coin_name="BNB"):
    """
    Calculate trading parameters based on live price.
    """
    current_price = get_live_price(coin_name)
    trade_amount = round(portfolio_value * 0.2 * confidence, 2)

    if action == "LONG":
        entry_price = current_price
        target_price = round(entry_price * 1.05, 2)
        stop_loss = round(entry_price * 0.97, 2)
    elif action == "SHORT":
        entry_price = current_price
        target_price = round(entry_price * 0.95, 2)
        stop_loss = round(entry_price * 1.03, 2)
    else:  # HOLD or uncertain action
        entry_price = current_price
        target_price = current_price
        stop_loss = current_price

    return {
        "amount": trade_amount,
        "entry_price": entry_price,
        "exit_price": target_price,
        "stop_loss": stop_loss,
        "current_price": current_price
    }
