# scorer.py

from config import WEIGHTS, THRESHOLDS, RED_FLAGS

def score_price_trend(change_7d: float) -> float:
    """Score based on 7-day price change. Range: 0–100."""
    if change_7d >= 20:  return 95
    if change_7d >= 10:  return 80
    if change_7d >= 3:   return 65
    if change_7d >= 0:   return 50
    if change_7d >= -10: return 30
    return 10

def score_volume(volume_to_mcap: float) -> float:
    """Volume/market cap ratio. High ratio = active trading."""
    if volume_to_mcap >= 0.30: return 90
    if volume_to_mcap >= 0.15: return 75
    if volume_to_mcap >= 0.05: return 55
    if volume_to_mcap >= 0.01: return 35
    return 15

def score_dev_activity(commits_4w: int) -> float:
    """GitHub commits in last 4 weeks."""
    if commits_4w >= 100: return 95
    if commits_4w >= 50:  return 80
    if commits_4w >= 20:  return 60
    if commits_4w >= 5:   return 40
    if commits_4w >= 1:   return 20
    return 0

def score_liquidity(volume_24h: float, market_cap: float) -> float:
    """Penalise micro-cap illiquid tokens — easy to manipulate."""
    if market_cap < 1_000_000:    return 10   # < $1M — extremely risky
    if market_cap < 10_000_000:   return 30   # < $10M
    if market_cap < 100_000_000:  return 55   # < $100M
    if market_cap < 1_000_000_000: return 75  # < $1B
    return 90                                  # large cap

def score_sentiment(reddit_subs: int, twitter_followers: int) -> float:
    """Rough community size proxy until we add real sentiment analysis."""
    combined = reddit_subs + twitter_followers
    if combined >= 500_000: return 85
    if combined >= 100_000: return 70
    if combined >= 10_000:  return 50
    if combined >= 1_000:   return 30
    return 15

def calculate_score(signals: dict, red_flags: list[str] = None) -> dict:
    """
    Main scoring function. Returns score, verdict, breakdown, and flags.
    """
    red_flags = red_flags or []

    # --- Individual sub-scores ---
    sub_scores = {
        "price_trend":      score_price_trend(signals["price_change_7d"]),
        "volume_spike":     score_volume(signals["volume_to_mcap"]),
        "dev_activity":     score_dev_activity(signals["github_commits_4w"]),
        "tokenomics":       50,   # placeholder — AI will fill this
        "liquidity":        score_liquidity(signals["volume_24h"], signals["market_cap"]),
        "social_sentiment": score_sentiment(signals["reddit_subscribers"], signals["twitter_followers"]),
        "news_sentiment":   50,   # placeholder — AI will fill this
    }

    # --- Weighted total ---
    total = sum(sub_scores[k] * WEIGHTS[k] for k in WEIGHTS)
    final_score = round(total)

    # --- Verdict ---
    has_red_flag = any(f in RED_FLAGS for f in red_flags)

    if has_red_flag:
        verdict = "AVOID"
    elif final_score >= THRESHOLDS["buy"]:
        verdict = "BUY"
    elif final_score >= THRESHOLDS["watch"]:
        verdict = "WATCH"
    else:
        verdict = "AVOID"

    return {
        "score":       final_score,
        "verdict":     verdict,
        "sub_scores":  sub_scores,
        "red_flags":   red_flags,
        "has_red_flag": has_red_flag,
    }