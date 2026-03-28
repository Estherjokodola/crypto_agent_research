# config.py

WEIGHTS = {
    "price_trend":   0.20,
    "volume_spike":  0.15,
    "dev_activity":  0.15,
    "tokenomics":    0.10,
    "liquidity":     0.10,
    "social_sentiment": 0.15,
    "news_sentiment":   0.15,
}

THRESHOLDS = {
    "buy":   70,
    "watch": 45,
}

# These override the score entirely — instant Avoid
RED_FLAGS = [
    "anonymous_team",
    "no_audit",
    "whale_dumping",
    "negative_news_spike",
]