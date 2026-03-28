# data_fetcher.py

import requests

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

def get_coin_data(coin_id: str) -> dict:
    """Fetch price, volume, market cap and 7d trend for a coin."""
    url = f"{COINGECKO_BASE}/coins/{coin_id}"
    params = {
        "localization": "false",
        "tickers": "false",
        "community_data": "true",
        "developer_data": "true",
        "sparkline": "false",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def extract_signals(raw: dict) -> dict:
    """Pull only the numbers we care about from the raw API response."""
    market = raw.get("market_data", {})
    dev    = raw.get("developer_data", {})
    comm   = raw.get("community_data", {})

    return {
        "name":             raw.get("name", "Unknown"),
        "symbol":           raw.get("symbol", "???").upper(),
        "price_usd":        market.get("current_price", {}).get("usd", 0),
        "price_change_7d":  market.get("price_change_percentage_7d", 0),
        "volume_24h":       market.get("total_volume", {}).get("usd", 0),
        "market_cap":       market.get("market_cap", {}).get("usd", 0),
        "volume_to_mcap":   (
            market.get("total_volume", {}).get("usd", 0) /
            max(market.get("market_cap", {}).get("usd", 1), 1)
        ),
        "github_commits_4w": dev.get("commit_count_4_weeks", 0),
        "github_stars":      dev.get("stars", 0),
        "reddit_subscribers": comm.get("reddit_subscribers", 0),
        "twitter_followers":  comm.get("twitter_followers", 0),
    }

if __name__ == "__main__":
    # Quick test — run: python data_fetcher.py
    data = get_coin_data("bitcoin")
    signals = extract_signals(data)
    for k, v in signals.items():
        print(f"{k:30s} {v}")