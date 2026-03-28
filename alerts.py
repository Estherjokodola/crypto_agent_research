# alerts.py

import time
import json
import os
from datetime import datetime
from data_fetcher import get_coin_data, extract_signals
from scorer import calculate_score
from ai_analyzer import analyze_with_ai

# ── Your watchlist — edit this freely ────────────────────────────────
WATCHLIST = [
    "bitcoin",
    "ethereum",
    "solana",
    "chainlink",
    "avalanche-2",
]

# ── Alert thresholds — tune these to your style ───────────────────────
ALERT_RULES = {
    "min_score_to_buy":      70,    # only alert BUY if score >= this
    "max_score_to_avoid":    45,    # alert AVOID if score drops below this
    "price_drop_alert":     -8.0,   # alert if 7d drop worse than this %
    "price_pump_alert":     12.0,   # alert if 7d pump better than this %
    "dev_dead_threshold":    5,     # alert if commits fall below this
}

HISTORY_FILE = "alert_history.json"

# ── Helpers ───────────────────────────────────────────────────────────
def load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE) as f:
            return json.load(f)
    return {}

def save_history(history: dict):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def already_alerted(history: dict, coin_id: str, alert_type: str) -> bool:
    """Avoid spamming the same alert repeatedly."""
    key = f"{coin_id}:{alert_type}"
    if key not in history:
        return False
    last = datetime.fromisoformat(history[key])
    hours_since = (datetime.now() - last).total_seconds() / 3600
    return hours_since < 12   # don't repeat same alert within 12 hours

def record_alert(history: dict, coin_id: str, alert_type: str):
    key = f"{coin_id}:{alert_type}"
    history[key] = datetime.now().isoformat()

def format_alert(level: str, coin: str, symbol: str, message: str) -> str:
    icons = {"BUY": "✅", "AVOID": "🚫", "WARNING": "⚠️", "INFO": "ℹ️"}
    icon  = icons.get(level, "•")
    ts    = datetime.now().strftime("%H:%M:%S")
    return f"[{ts}]  {icon}  {level:7s}  {symbol:6s}  {message}"

# ── Core alert logic ──────────────────────────────────────────────────
def check_coin(coin_id: str, history: dict) -> list[str]:
    """Analyze one coin and return list of triggered alerts."""
    alerts = []

    try:
        raw        = get_coin_data(coin_id)
        signals    = extract_signals(raw)
        first_pass = calculate_score(signals)
        ai         = analyze_with_ai(signals, first_pass["sub_scores"])

        first_pass["sub_scores"]["tokenomics"]     = ai["tokenomics_score"]
        first_pass["sub_scores"]["news_sentiment"] = ai["news_sentiment_score"]
        final = calculate_score(signals, red_flags=ai["red_flags"])

        score   = final["score"]
        verdict = final["verdict"]
        name    = signals["name"]
        symbol  = signals["symbol"]
        chg     = signals["price_change_7d"]
        commits = signals["github_commits_4w"]

        # ── Rule 1: Strong buy signal ─────────────────────────────────
        if score >= ALERT_RULES["min_score_to_buy"] and verdict == "BUY":
            if not already_alerted(history, coin_id, "BUY"):
                alerts.append(format_alert(
                    "BUY", name, symbol,
                    f"Score {score}/100 — {ai['key_opportunity']}"
                ))
                record_alert(history, coin_id, "BUY")

        # ── Rule 2: Avoid signal ──────────────────────────────────────
        if score <= ALERT_RULES["max_score_to_avoid"] or verdict == "AVOID":
            if not already_alerted(history, coin_id, "AVOID"):
                alerts.append(format_alert(
                    "AVOID", name, symbol,
                    f"Score {score}/100 — {ai['key_risk']}"
                ))
                record_alert(history, coin_id, "AVOID")

        # ── Rule 3: Sharp price drop ──────────────────────────────────
        if chg <= ALERT_RULES["price_drop_alert"]:
            if not already_alerted(history, coin_id, "DROP"):
                alerts.append(format_alert(
                    "WARNING", name, symbol,
                    f"Down {chg:.1f}% in 7 days — possible breakdown"
                ))
                record_alert(history, coin_id, "DROP")

        # ── Rule 4: Sharp price pump ──────────────────────────────────
        if chg >= ALERT_RULES["price_pump_alert"]:
            if not already_alerted(history, coin_id, "PUMP"):
                alerts.append(format_alert(
                    "INFO", name, symbol,
                    f"Up {chg:.1f}% in 7 days — momentum building"
                ))
                record_alert(history, coin_id, "PUMP")

        # ── Rule 5: Dead development ──────────────────────────────────
        if commits <= ALERT_RULES["dev_dead_threshold"]:
            if not already_alerted(history, coin_id, "DEV_DEAD"):
                alerts.append(format_alert(
                    "WARNING", name, symbol,
                    f"Only {commits} GitHub commits in 4 weeks — dev activity dying"
                ))
                record_alert(history, coin_id, "DEV_DEAD")

        # ── Rule 6: Red flags ─────────────────────────────────────────
        if final["red_flags"]:
            flag_str = ", ".join(final["red_flags"])
            if not already_alerted(history, coin_id, "REDFLAG"):
                alerts.append(format_alert(
                    "AVOID", name, symbol,
                    f"Red flags detected: {flag_str}"
                ))
                record_alert(history, coin_id, "REDFLAG")

    except Exception as e:
        alerts.append(f"  [ERROR] Could not analyze {coin_id}: {e}")

    return alerts

# ── Main loop ─────────────────────────────────────────────────────────
def run_alerts(interval_minutes: int = 60):
    """
    Run continuously, checking every `interval_minutes`.
    Default: every 60 minutes.
    """
    print("\n" + "=" * 60)
    print("  Crypto Alert System — running")
    print(f"  Watchlist: {', '.join(WATCHLIST)}")
    print(f"  Check interval: every {interval_minutes} minutes")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    while True:
        now     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history = load_history()
        triggered = []

        print(f"\n  Checking watchlist at {now}...")

        for coin_id in WATCHLIST:
            alerts = check_coin(coin_id, history)
            triggered.extend(alerts)
            time.sleep(2)   # be polite to CoinGecko's free API rate limit

        save_history(history)

        if triggered:
            print("\n  ── ALERTS ──────────────────────────────────────────")
            for alert in triggered:
                print(f"  {alert}")
            print("  ────────────────────────────────────────────────────")
        else:
            print("  No new alerts. All coins within normal parameters.")

        print(f"\n  Next check in {interval_minutes} minutes. Ctrl+C to stop.")
        time.sleep(interval_minutes * 60)

# ── Single run mode ───────────────────────────────────────────────────
def run_once():
    """Run a single check and exit — useful for testing."""
    history   = load_history()
    triggered = []

    print("\nRunning single alert check...")
    print("-" * 60)

    for coin_id in WATCHLIST:
        print(f"  Checking {coin_id}...")
        alerts = check_coin(coin_id, history)
        triggered.extend(alerts)
        time.sleep(2)

    save_history(history)

    print("\n── Results ─────────────────────────────────────────────────")
    if triggered:
        for alert in triggered:
            print(f"  {alert}")
    else:
        print("  No alerts triggered.")
    print("─" * 60)

if __name__ == "__main__":
    import sys
    if "--once" in sys.argv:
        run_once()
    else:
        interval = int(sys.argv[1]) if len(sys.argv) > 1 else 60
        run_alerts(interval_minutes=interval)