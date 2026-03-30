# main.py

from data_fetcher import get_coin_data, extract_signals
from scorer import calculate_score
from ai_analyzer import analyze_with_ai

def analyze_coin(coin_id: str):
    print(f"\nAnalyzing {coin_id.upper()}...")
    print("=" * 50)

    # 1. Fetch data
    print("  Fetching data from CoinGecko...")
    raw     = get_coin_data(coin_id)
    signals = extract_signals(raw)

    # 2. First pass score (no AI yet)
    first_pass = calculate_score(signals)

    # 3. AI analysis — fills in tokenomics + news sentiment + red flags
    print("  Running AI analysis...")
    ai = analyze_with_ai(signals, first_pass["sub_scores"])

    # 4. Inject AI scores back into sub_scores and recalculate
    first_pass["sub_scores"]["tokenomics"]      = ai["tokenomics_score"]
    first_pass["sub_scores"]["news_sentiment"]  = ai["news_sentiment_score"]
    final = calculate_score(signals, red_flags=ai["red_flags"])
    final["sub_scores"]["tokenomics"]     = ai["tokenomics_score"]
    final["sub_scores"]["news_sentiment"] = ai["news_sentiment_score"]

    # 5. Print full report
    print_report(signals, final, ai)

def print_report(signals: dict, result: dict, ai: dict):
    name    = signals['name']
    symbol  = signals['symbol']
    score   = result['score']
    verdict = result['verdict']

    verdict_icon = {"BUY": "✅", "WATCH": "👀", "AVOID": "🚫"}.get(verdict, "")

    print(f"\n  {name} ({symbol})")
    print(f"  Price:   ${signals['price_usd']:,.4f}   7d: {signals['price_change_7d']:+.1f}%")
    print(f"  MCap:    ${signals['market_cap']:,.0f}")
    print()
    print(f"  SCORE:   {score}/100")
    print(f"  VERDICT: {verdict_icon} {verdict}")
    print()
    print(f"  {ai['summary']}")
    print()
    print("  Score breakdown:")
    for k, v in result['sub_scores'].items():
        bar  = "█" * (v // 10) + "░" * (10 - v // 10)
        print(f"    {k:22s} {bar} {v:3d}")
    print()
    print(f"  Key risk:        {ai['key_risk']}")
    print(f"  Key opportunity: {ai['key_opportunity']}")

    if result['red_flags']:
        print(f"\n  ⚠️  RED FLAGS: {', '.join(result['red_flags'])}")

    print("\n" + "-" * 50)


if __name__ == "__main__":
    coins = ["bitcoin", "ethereum", "solana"]
    for coin in coins:
        analyze_coin(coin)