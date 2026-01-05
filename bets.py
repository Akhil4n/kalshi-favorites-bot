import requests
import datetime
import trading

# Getting NBA contracts for today's games
def get_nba_markets():
    url = "https://api.elections.kalshi.com/trade-api/v2/markets"
    params = {
        "series_ticker": "KXNBAGAME",
        "status": "open",
    }

    response = requests.get(url, params=params)
    response_data = response.json()
    markets = response_data.get("markets", [])

    filtered_markets = []

    # Get "today" string in format YYMMMDD (e.g. 25DEC29)
    now = datetime.datetime.now()
    today_str = now.strftime("%y%b%d").upper()

    for market in markets:
        ticker = market.get("ticker", "")
        # Ticker format: KXNBAGAME-YYMMMDD...
        # Example: KXNBAGAME-25DEC29MILCHA-MIL
        if f"KXNBAGAME-{today_str}" in ticker:
            filtered_markets.append(market)
    games = []
    for market in filtered_markets:
        games.append({
            "title": market.get("title", ""),
            "ticker": market.get("ticker", ""),
            "yes_ask": market.get("yes_ask", 0),
            "no_ask": market.get("no_ask", 0),
        })
    return games

def get_valid_bet_tickers(games):
    bet_tickers = []
    for game in games:
        price = game.get("yes_ask")
        #Could change limits as needed to optimize
        if price >= 75 and price <= 87:
            bet_tickers.append(game.get("ticker", ""))
    return bet_tickers

def get_valid_sell_tickers(games, open_positions):
    opset = set(open_positions)
    sell_tickers = []
    for game in games:
        if game.get("ticker", "") in opset and game.get("yes_ask") <= 40:
            sell_tickers.append(game.get("ticker", ""))
    return sell_tickers