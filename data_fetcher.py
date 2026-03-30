# data_fetcher.py

import time
import requests

COINGECKO_BASE = "https://api.coingecko.com/api/v3"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
}

def get_coin_data(coin_id: str, retries: int = 3) -> dict:
    """Fetch coin data with retry logic and proper headers."""
    url = f"{COINGECKO_BASE}/coins/{coin_id}"
    params = {
        "localization":    "false",
        "tickers":         "false",
        "community_data":  "true",
        "developer_data":  "true",
        "sparkline":       "false",
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, params=params, headers=HEADERS, timeout=15)

            # Rate limited — wait and retry
            if response.status_code == 429:
                wait = 60 * (attempt + 1)
                print(f"  Rate limited. Waiting {wait}s before retry {attempt+1}/{retries}...")
                time.sleep(wait)
                continue

            # Coin not found
            if response.status_code == 404:
                raise ValueError(f"Coin '{coin_id}' not found on CoinGecko. Check the ID.")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            print(f"  Timeout on attempt {attempt+1}/{retries}. Retrying...")
            time.sleep(10)
            continue

        except requests.exceptions.ConnectionError:
            print(f"  Connection error on attempt {attempt+1}/{retries}. Retrying...")
            time.sleep(15)
            continue

    raise Exception(f"Failed to fetch data for '{coin_id}' after {retries} attempts.")

def extract_signals(raw: dict) -> dict:
    """Pull only the numbers we care about from the raw API response."""
    market = raw.get("market_data", {})
    dev    = raw.get("developer_data", {})
    comm   = raw.get("community_data", {})

    return {
        "name":              raw.get("name", "Unknown"),
        "symbol":            raw.get("symbol", "???").upper(),
        "price_usd":         market.get("current_price", {}).get("usd", 0),
        "price_change_7d":   market.get("price_change_percentage_7d", 0),
        "volume_24h":        market.get("total_volume", {}).get("usd", 0),
        "market_cap":        market.get("market_cap", {}).get("usd", 0),
        "volume_to_mcap": (
            market.get("total_volume", {}).get("usd", 0) /
            max(market.get("market_cap", {}).get("usd", 1), 1)
        ),
        "github_commits_4w": dev.get("commit_count_4_weeks", 0),
        "github_stars":      dev.get("stars", 0),
        "reddit_subscribers": comm.get("reddit_subscribers", 0),
        "twitter_followers":  comm.get("twitter_followers", 0),
    }

if __name__ == "__main__":
    data    = get_coin_data("bitcoin")
    signals = extract_signals(data)
    for k, v in signals.items():
        print(f"{k:30s} {v}")