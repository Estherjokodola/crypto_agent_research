# dashboard.py

import streamlit as st

@st.cache_data(ttl=300)
def run_full_analysis(coin_id: str):
    from data_fetcher import get_coin_data, extract_signals
    from scorer import calculate_score
    from ai_analyzer import analyze_with_ai

    raw        = get_coin_data(coin_id)
    signals    = extract_signals(raw)
    first_pass = calculate_score(signals)
    ai         = analyze_with_ai(signals, first_pass["sub_scores"])

    first_pass["sub_scores"]["tokenomics"]     = ai["tokenomics_score"]
    first_pass["sub_scores"]["news_sentiment"] = ai["news_sentiment_score"]
    final = calculate_score(signals, red_flags=ai["red_flags"])
    final["sub_scores"]["tokenomics"]     = ai["tokenomics_score"]
    final["sub_scores"]["news_sentiment"] = ai["news_sentiment_score"]

    return signals, final, ai

st.set_page_config(
    page_title="Crypto Research Agent",
    page_icon="📊",
    layout="wide"
)

# ── Styling ──────────────────────────────────────────────────────────
st.markdown("""
<style>
.verdict-buy   { background:#d4edda; color:#155724; padding:6px 18px; border-radius:8px; font-weight:600; font-size:1.1rem; }
.verdict-watch { background:#fff3cd; color:#856404; padding:6px 18px; border-radius:8px; font-weight:600; font-size:1.1rem; }
.verdict-avoid { background:#f8d7da; color:#721c24; padding:6px 18px; border-radius:8px; font-weight:600; font-size:1.1rem; }
.flag-box      { background:#f8d7da; color:#721c24; padding:4px 12px; border-radius:6px; font-size:0.85rem; margin:2px; display:inline-block; }
.metric-label  { font-size:0.78rem; color:#888; margin-bottom:2px; }
.metric-value  { font-size:1.4rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────
st.title("📊 Crypto Research Agent")
st.caption("Short-term trading signals · Powered by CoinGecko + GROK AI")
st.divider()

# ── Sidebar — coin selector ──────────────────────────────────────────
with st.sidebar:
    st.header("Analyze a coin")

    popular = ["bitcoin", "ethereum", "solana", "cardano", "polkadot",
               "avalanche-2", "chainlink", "uniswap", "dogecoin", "shiba-inu"]

    selected = st.selectbox("Pick a popular coin", popular)
    custom   = st.text_input("Or type any CoinGecko ID", placeholder="e.g. pepe, sui, aptos")

    coin_id = custom.strip().lower() if custom.strip() else selected

    analyze_btn = st.button("Analyze", type="primary", use_container_width=True)

    st.divider()
    st.caption("Coin IDs from coingecko.com/en/coins — use the URL slug")

# ── Main panel ───────────────────────────────────────────────────────
if analyze_btn:
    try:
        with st.spinner(f"Analyzing {coin_id}..."):
            signals, final, ai = run_full_analysis(coin_id)
    except ValueError as e:
        st.error(str(e))
        st.stop()
    except Exception as e:
        st.error("Could not fetch data. Wait 60 seconds and try again.")
        st.stop()

    # ── Coin header ──────────────────────────────────────────────────
    col_name, col_price, col_change, col_mcap = st.columns([2, 1.5, 1.5, 2])

    with col_name:
        st.markdown(f"### {signals['name']} ({signals['symbol']})")

    with col_price:
        st.markdown('<p class="metric-label">Price (USD)</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">${signals["price_usd"]:,.4f}</p>', unsafe_allow_html=True)

    with col_change:
        change = signals["price_change_7d"]
        color  = "green" if change >= 0 else "red"
        st.markdown('<p class="metric-label">7-day change</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value" style="color:{color}">{change:+.1f}%</p>', unsafe_allow_html=True)

    with col_mcap:
        mcap = signals["market_cap"]
        if mcap >= 1e9:
            mcap_str = f"${mcap/1e9:.1f}B"
        elif mcap >= 1e6:
            mcap_str = f"${mcap/1e6:.1f}M"
        else:
            mcap_str = f"${mcap:,.0f}"
        st.markdown('<p class="metric-label">Market cap</p>', unsafe_allow_html=True)
        st.markdown(f'<p class="metric-value">{mcap_str}</p>', unsafe_allow_html=True)

    st.divider()

    # ── Score + verdict ──────────────────────────────────────────────
    col_score, col_verdict, col_summary = st.columns([1, 1, 3])

    score   = final["score"]
    verdict = final["verdict"]

    with col_score:
        st.metric("Overall score", f"{score} / 100")
        st.progress(score / 100)

    with col_verdict:
        st.markdown("**Verdict**")
        css_class = {"BUY": "verdict-buy", "WATCH": "verdict-watch", "AVOID": "verdict-avoid"}.get(verdict, "verdict-watch")
        icon       = {"BUY": "✅ BUY", "WATCH": "👀 WATCH", "AVOID": "🚫 AVOID"}.get(verdict, verdict)
        st.markdown(f'<span class="{css_class}">{icon}</span>', unsafe_allow_html=True)

    with col_summary:
        st.markdown("**Analysis**")
        st.write(ai["summary"])

    st.divider()

    # ── Score breakdown ──────────────────────────────────────────────
    st.subheader("Score breakdown")

    sub = final["sub_scores"]
    labels = {
        "price_trend":      "Price trend (7d)",
        "volume_spike":     "Volume spike",
        "dev_activity":     "Developer activity",
        "tokenomics":       "Tokenomics",
        "liquidity":        "Liquidity",
        "social_sentiment": "Social sentiment",
        "news_sentiment":   "News sentiment",
    }
    colors = {
        "price_trend":      "#7F77DD",
        "volume_spike":     "#7F77DD",
        "dev_activity":     "#1D9E75",
        "tokenomics":       "#1D9E75",
        "liquidity":        "#1D9E75",
        "social_sentiment": "#EF9F27",
        "news_sentiment":   "#EF9F27",
    }

    for key, label in labels.items():
        val = sub.get(key, 50)
        col_lbl, col_bar, col_num = st.columns([2, 5, 0.7])
        with col_lbl:
            st.caption(label)
        with col_bar:
            st.progress(val / 100)
        with col_num:
            st.caption(f"**{val}**")

    st.divider()

    # ── Risk / Opportunity ───────────────────────────────────────────
    col_risk, col_opp = st.columns(2)

    with col_risk:
        st.markdown("#### Key risk")
        st.error(ai["key_risk"])

    with col_opp:
        st.markdown("#### Key opportunity")
        st.success(ai["key_opportunity"])

    # ── Red flags ────────────────────────────────────────────────────
    if final["red_flags"]:
        st.divider()
        st.markdown("#### ⚠️ Red flags detected")
        flag_labels = {
            "anonymous_team":      "Anonymous team",
            "no_audit":            "No smart contract audit",
            "whale_dumping":       "Whale wallet dumping",
            "negative_news_spike": "Negative news spike",
        }
        for f in final["red_flags"]:
            st.markdown(f'<span class="flag-box">🚩 {flag_labels.get(f, f)}</span>', unsafe_allow_html=True)
        st.warning("One or more red flags override the score — verdict forced to AVOID.")

    # ── Raw signals expander ─────────────────────────────────────────
    with st.expander("Raw signal data"):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Market data**")
            st.write(f"24h Volume: ${signals['volume_24h']:,.0f}")
            st.write(f"Vol/MCap ratio: {signals['volume_to_mcap']:.3f}")
            st.write(f"Reddit subscribers: {signals['reddit_subscribers']:,}")
            st.write(f"Twitter followers: {signals['twitter_followers']:,}")
        with col2:
            st.write("**Developer data**")
            st.write(f"GitHub commits (4w): {signals['github_commits_4w']}")
            st.write(f"GitHub stars: {signals['github_stars']:,}")

else:
    # ── Empty state ──────────────────────────────────────────────────
    st.markdown("""
    ### How to use
    1. Pick a coin from the sidebar or type any CoinGecko ID
    2. Click **Analyze**
    3. Get your score, verdict, and plain-English reasoning

    **Supported coins:** Any coin listed on CoinGecko.
    Use the ID from the URL — e.g. `coingecko.com/en/coins/bitcoin` → ID is `bitcoin`
    """)

    st.info("Try starting with: bitcoin · ethereum · solana · pepe · chainlink")