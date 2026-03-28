# ai_analyzer.py — smart rule-based analyzer (no API key needed)

def analyze_with_ai(signals: dict, sub_scores: dict) -> dict:
    """
    Rule-based analyzer that mimics AI reasoning.
    Reads signal combinations and generates human-readable output.
    """
    name   = signals["name"]
    symbol = signals["symbol"]

    price_7d    = signals["price_change_7d"]
    vol_ratio   = signals["volume_to_mcap"]
    commits     = signals["github_commits_4w"]
    mcap        = signals["market_cap"]
    reddit      = signals["reddit_subscribers"]
    twitter     = signals["twitter_followers"]

    p_score  = sub_scores["price_trend"]
    v_score  = sub_scores["volume_spike"]
    d_score  = sub_scores["dev_activity"]
    l_score  = sub_scores["liquidity"]
    s_score  = sub_scores["social_sentiment"]

    red_flags = []
    observations = []
    risks = []
    opportunities = []

    # ── Red flag detection ──────────────────────────────────────────

    # Anonymous team proxy: tiny community + no dev activity
    if reddit < 500 and commits == 0 and mcap < 5_000_000:
        red_flags.append("anonymous_team")

    # No audit proxy: micro-cap with zero dev activity
    if mcap < 2_000_000 and commits == 0:
        red_flags.append("no_audit")

    # Whale dumping proxy: high volume but price crashing hard
    if vol_ratio > 0.25 and price_7d < -15:
        red_flags.append("whale_dumping")

    # Negative news proxy: large community but price + sentiment both bad
    if s_score < 25 and price_7d < -10 and reddit > 10_000:
        red_flags.append("negative_news_spike")

    # ── Tokenomics score ────────────────────────────────────────────

    tok = 50  # base

    if mcap > 1_000_000_000:   tok += 20   # large cap = safer supply
    elif mcap > 100_000_000:   tok += 10
    elif mcap < 5_000_000:     tok -= 20   # micro-cap = risky

    if vol_ratio > 0.15:       tok += 15   # healthy trading activity
    elif vol_ratio < 0.02:     tok -= 15   # illiquid = dangerous

    if commits > 50:           tok += 10   # active dev = real project
    elif commits == 0:         tok -= 15   # no dev = red flag

    tokenomics_score = max(0, min(100, tok))

    # ── News sentiment score ────────────────────────────────────────

    news = 50  # base

    if price_7d > 10:          news += 20
    elif price_7d > 3:         news += 10
    elif price_7d < -10:       news -= 20
    elif price_7d < -5:        news -= 10

    community = reddit + twitter
    if community > 500_000:    news += 15
    elif community > 50_000:   news += 8
    elif community < 1_000:    news -= 15

    if commits > 50:           news += 10
    elif commits == 0:         news -= 10

    news_sentiment_score = max(0, min(100, news))

    # ── Observation builder ─────────────────────────────────────────

    # Price momentum
    if p_score >= 80:
        observations.append(f"strong upward momentum (+{price_7d:.1f}% in 7 days)")
        opportunities.append(f"momentum continuation — {symbol} is trending with volume confirmation")
    elif p_score >= 60:
        observations.append(f"mild positive trend (+{price_7d:.1f}% in 7 days)")
        opportunities.append("early positioning before potential breakout")
    elif p_score <= 30:
        observations.append(f"notable price decline ({price_7d:.1f}% in 7 days)")
        risks.append(f"continued downtrend — {symbol} has lost momentum this week")
    else:
        observations.append("price is largely flat this week")

    # Volume
    if v_score >= 75:
        observations.append("volume is significantly elevated vs market cap")
        opportunities.append("high volume confirms price moves are real, not thin-air trading")
    elif v_score <= 30:
        observations.append("low trading volume relative to market cap")
        risks.append("thin liquidity means price moves can be easily manipulated")

    # Developer activity
    if d_score >= 80:
        observations.append(f"very active development ({commits} commits in 4 weeks)")
    elif d_score >= 50:
        observations.append(f"moderate development activity ({commits} commits in 4 weeks)")
    elif d_score <= 20:
        observations.append("little to no developer activity recently")
        risks.append("low dev activity suggests the project may be stagnating or abandoned")

    # Liquidity
    if l_score >= 80:
        observations.append("large market cap provides solid liquidity")
    elif l_score <= 30:
        observations.append("small market cap — low liquidity, high slippage risk")
        risks.append("micro-cap size makes this vulnerable to pump-and-dump dynamics")

    # Community
    if s_score >= 70:
        observations.append(f"strong community ({(reddit+twitter):,} combined followers)")
    elif s_score <= 25:
        observations.append("very small community presence")
        risks.append("minimal community means low organic buying pressure")

    # ── Contradiction detector (hype vs reality) ────────────────────

    if p_score >= 70 and d_score <= 20:
        observations.append("price is rising but developer activity is low — possible hype cycle")
        risks.append("price action may not be backed by real development progress")

    if d_score >= 80 and p_score <= 30:
        observations.append("strong development despite price drop — possible undervaluation")
        opportunities.append("dev activity is strong — price weakness may be a buying opportunity")

    if v_score >= 75 and p_score <= 30:
        risks.append("high volume during a price drop often signals distribution — be cautious")

    # ── Build summary ───────────────────────────────────────────────

    # Pick top 2 observations for the summary
    obs_text = ". ".join(observations[:2]).capitalize()
    if not obs_text:
        obs_text = "Signals are mixed with no strong directional bias"

    # Pick best risk and opportunity
    key_risk        = risks[0]        if risks        else "No major red flags detected in current data"
    key_opportunity = opportunities[0] if opportunities else "Monitor for a momentum shift before entering"

    # Tone the summary based on overall signal strength
    avg_score = (p_score + v_score + d_score + l_score + s_score) / 5

    if red_flags:
        tone = f"Exercise extreme caution with {name}."
    elif avg_score >= 70:
        tone = f"{name} shows strong signals for short-term positioning."
    elif avg_score >= 50:
        tone = f"{name} presents a mixed picture — selective entry may be appropriate."
    else:
        tone = f"{name} does not present a compelling short-term setup right now."

    summary = f"{tone} {obs_text}. For short-term traders, the key factor to watch is {key_risk.lower()}."

    return {
        "tokenomics_score":     tokenomics_score,
        "news_sentiment_score": news_sentiment_score,
        "red_flags":            red_flags,
        "summary":              summary,
        "key_risk":             key_risk,
        "key_opportunity":      key_opportunity,
    }