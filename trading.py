import headers
import requests

def get_open_positions():
    path = "/trade-api/v2/portfolio/positions"
    url = "https://api.elections.kalshi.com" + path
    header = headers.get_headers(path, "GET")
    response = requests.get(url, headers=header)
    tickers = set()
    for position in response.json().get("market_positions", []):
        tickers.add(position.get("ticker", ""))
    return tickers

def place_bet(tickers, open_positions) -> list:
    order_ids = []
    path = "/trade-api/v2/portfolio/orders"
    url = "https://api.elections.kalshi.com" + path
    for ticker in tickers:
        if ticker in open_positions:
            continue
        header = headers.get_headers(path, "POST")
        payload = {
            "ticker": ticker,
            "side": "yes",
            "action": "buy",
            "count": 1,
            "type": "market",
            "yes_price": 87 # May need to change this later?
        }
        response = requests.post(url, headers=header, json=payload)
        o_id = response.json().get("order", {}).get("order_id", "")
        order_ids.append((ticker, o_id))
    return order_ids

def place_sells(sell_tickers, sells) -> list:
    order_ids = []
    path = "/trade-api/v2/portfolio/orders"
    url = "https://api.elections.kalshi.com" + path
    for ticker in sell_tickers:
        if ticker in sells:
            continue
        header = headers.get_headers(path, "POST")
        payload = {
            "ticker": ticker,
            "side": "yes",
            "action": "sell",
            "count": 1,
            "type": "market",
            "yes_price": 35 # May need to change this later?
        }
        response = requests.post(url, headers=header, json=payload)
        o_id = response.json().get("order", {}).get("order_id", "")
        order_ids.append((ticker, o_id))
        sells.add(ticker)
    return order_ids