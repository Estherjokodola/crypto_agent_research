# ai_analyzer.py — powered by Groq (free) + Llama 3

import os
import json

try:
    import streamlit as st
    GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from groq import Groq
client = Groq(api_key=GROQ_API_KEY)

def build_prompt(signals: dict, sub_scores: dict) -> str:
    return f"""
You are a crypto research analyst helping a short-term trader (days to weeks timeframe).
Analyze this project and return a structured JSON assessment.

--- PROJECT DATA ---
Name:                {signals['name']} ({signals['symbol']})
Price (USD):         ${signals['price_usd']:,.4f}
7-day price change:  {signals['price_change_7d']:+.1f}%
24h volume:          ${signals['volume_24h']:,.0f}
Market cap:          ${signals['market_cap']:,.0f}
Volume/MCap ratio:   {signals['volume_to_mcap']:.3f}
GitHub commits (4w): {signals['github_commits_4w']}
GitHub stars:        {signals['github_stars']}
Reddit subscribers:  {signals['reddit_subscribers']:,}
Twitter followers:   {signals['twitter_followers']:,}

--- CURRENT SCORE BREAKDOWN ---
Price trend score:   {sub_scores['price_trend']}/100
Volume score:        {sub_scores['volume_spike']}/100
Dev activity score:  {sub_scores['dev_activity']}/100
Liquidity score:     {sub_scores['liquidity']}/100
Sentiment score:     {sub_scores['social_sentiment']}/100

--- YOUR TASK ---
Assess this project for a SHORT-TERM trader (days to weeks timeframe).
Return ONLY valid JSON with exactly these fields, no extra text, no markdown:

{{
  "tokenomics_score": <integer 0-100>,
  "news_sentiment_score": <integer 0-100>,
  "red_flags": <list of strings, can be empty>,
  "summary": "<2-3 sentence plain English verdict for a trader>",
  "key_risk": "<single biggest risk right now>",
  "key_opportunity": "<single biggest opportunity right now>"
}}

For red_flags, only use these exact strings if applicable:
- "anonymous_team"
- "no_audit"
- "whale_dumping"
- "negative_news_spike"

Base tokenomics_score on: market cap size, volume/mcap ratio, and liquidity.
Base news_sentiment_score on: community size, dev activity, and overall momentum.
Be direct and honest. Short-term traders need clear signals, not hedged language.
"""

def analyze_with_ai(signals: dict, sub_scores: dict) -> dict:
    """Send data to Groq (Llama 3) and get back AI-powered analysis."""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",   # free, fast, good enough for this task
            messages=[
                {
                    "role": "system",
                    "content": "You are a crypto analyst. Always respond with valid JSON only. No markdown, no explanation outside the JSON."
                },
                {
                    "role": "user",
                    "content": build_prompt(signals, sub_scores)
                }
            ],
            temperature=0.3,
            max_tokens=500,
        )

        raw = response.choices[0].message.content.strip()

        # Strip markdown fences if model adds them
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        result = json.loads(raw)

        # Validate and clamp all scores to 0-100
        result["tokenomics_score"]     = max(0, min(100, int(result.get("tokenomics_score", 50))))
        result["news_sentiment_score"] = max(0, min(100, int(result.get("news_sentiment_score", 50))))
        result["red_flags"]            = result.get("red_flags", [])
        result["summary"]              = result.get("summary", "No summary available.")
        result["key_risk"]             = result.get("key_risk", "Unknown")
        result["key_opportunity"]      = result.get("key_opportunity", "Unknown")

        return result

    except json.JSONDecodeError as e:
        print(f"  [AI] JSON parse error: {e}")
        return _fallback()
    except Exception as e:
        print(f"  [AI] Error: {e}")
        return _fallback()

def _fallback() -> dict:
    """Safe defaults if AI call fails — tool still works without AI."""
    return {
        "tokenomics_score":     50,
        "news_sentiment_score": 50,
        "red_flags":            [],
        "summary":              "AI analysis unavailable. Scores based on on-chain data only.",
        "key_risk":             "Unable to assess",
        "key_opportunity":      "Unable to assess",
    }