# pages/compare.py

import streamlit as st
from data_fetcher import get_coin_data, extract_signals
from scorer import calculate_score
from ai_analyzer import analyze_with_ai

st.set_page_config(page_title="Compare Coins", page_icon="⚖️", layout="wide")

st.title("⚖️ Multi-coin comparison")
st.caption("Analyze up to 5 coins side by side and rank them by score")
st.divider()

# ── Coin input ────────────────────────────────────────────────────────
st.markdown("#### Enter coins to compare")
cols = st.columns(5)
coin_inputs = []
defaults = ["bitcoin", "ethereum", "solana", "", ""]
for i, col in enumerate(cols):
    with col:
        val = col.text_input(f"Coin {i+1}", value=defaults[i], placeholder="e.g. pepe")
        coin_inputs.append(val.strip().lower())

coins_to_analyze = [c for c in coin_inputs if c]

run_btn = st.button("Compare all", type="primary")

# ── Analysis ──────────────────────────────────────────────────────────
if run_btn and coins_to_analyze:

    results = []
    progress = st.progress(0)
    status   = st.empty()

    for i, coin_id in enumerate(coins_to_analyze):
        status.caption(f"Analyzing {coin_id}...")
        try:
            raw        = get_coin_data(coin_id)
            signals    = extract_signals(raw)
            first_pass = calculate_score(signals)
            ai         = analyze_with_ai(signals, first_pass["sub_scores"])

            first_pass["sub_scores"]["tokenomics"]     = ai["tokenomics_score"]
            first_pass["sub_scores"]["news_sentiment"] = ai["news_sentiment_score"]
            final = calculate_score(signals, red_flags=ai["red_flags"])
            final["sub_scores"]["tokenomics"]     = ai["tokenomics_score"]
            final["sub_scores"]["news_sentiment"] = ai["news_sentiment_score"]

            results.append({
                "coin_id": coin_id,
                "signals": signals,
                "result":  final,
                "ai":      ai,
            })
        except Exception as e:
            st.warning(f"Could not fetch '{coin_id}': {e}")

        progress.progress((i + 1) / len(coins_to_analyze))

    status.empty()
    progress.empty()

    if not results:
        st.error("No coins could be analyzed. Check the IDs and try again.")
        st.stop()

    # Sort by score descending
    results.sort(key=lambda x: x["result"]["score"], reverse=True)

    st.divider()

    # ── Ranking header ────────────────────────────────────────────────
    st.subheader("Ranking — best setup right now")

    verdict_css = {
        "BUY":   ("✅ BUY",   "#d4edda", "#155724"),
        "WATCH": ("👀 WATCH", "#fff3cd", "#856404"),
        "AVOID": ("🚫 AVOID", "#f8d7da", "#721c24"),
    }

    sub_labels = {
        "price_trend":      "Price",
        "volume_spike":     "Volume",
        "dev_activity":     "Dev",
        "tokenomics":       "Tokenomics",
        "liquidity":        "Liquidity",
        "social_sentiment": "Social",
        "news_sentiment":   "News",
    }

    # ── Summary table ─────────────────────────────────────────────────
    header = st.columns([0.4, 1.8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.2])
    headers = ["#", "Coin", "Score", "Price", "7d %",
               "Price", "Vol", "Dev", "Tok", "Liq", "Social", "Verdict"]
    for col, h in zip(header, headers):
        col.markdown(f"**{h}**")

    st.markdown('<hr style="margin:4px 0;border-color:#eee">', unsafe_allow_html=True)

    for rank, r in enumerate(results, 1):
        sig = r["signals"]
        res = r["result"]
        sub = res["sub_scores"]
        verdict = res["verdict"]
        icon, bg, fg = verdict_css.get(verdict, ("?", "#eee", "#333"))

        row = st.columns([0.4, 1.8, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1.2])

        row[0].markdown(f"**{rank}**")
        row[1].markdown(f"**{sig['name']}** `{sig['symbol']}`")
        row[2].markdown(f"**{res['score']}**")

        price_str = f"${sig['price_usd']:,.2f}" if sig['price_usd'] > 1 else f"${sig['price_usd']:,.6f}"
        row[3].caption(price_str)

        chg = sig['price_change_7d']
        chg_color = "green" if chg >= 0 else "red"
        row[4].markdown(f"<span style='color:{chg_color}'>{chg:+.1f}%</span>", unsafe_allow_html=True)

        for i, key in enumerate(sub_labels.keys()):
            val = sub.get(key, 50)
            bar_color = "#7F77DD" if key in ["price_trend","volume_spike"] else \
                        "#1D9E75" if key in ["dev_activity","tokenomics","liquidity"] else "#EF9F27"
            row[5 + i].markdown(
                f"<div style='background:#eee;border-radius:4px;height:6px;margin-top:6px'>"
                f"<div style='width:{val}%;background:{bar_color};height:6px;border-radius:4px'></div>"
                f"</div><span style='font-size:11px;color:#888'>{val}</span>",
                unsafe_allow_html=True
            )

        row[11].markdown(
            f"<span style='background:{bg};color:{fg};padding:2px 8px;"
            f"border-radius:6px;font-size:12px;font-weight:600'>{icon}</span>",
            unsafe_allow_html=True
        )

        st.markdown('<hr style="margin:4px 0;border-color:#f0f0f0">', unsafe_allow_html=True)

    # ── Detail cards ──────────────────────────────────────────────────
    st.divider()
    st.subheader("Full breakdown")

    for r in results:
        sig     = r["signals"]
        res     = r["result"]
        ai      = r["ai"]
        verdict = res["verdict"]
        icon, bg, fg = verdict_css.get(verdict, ("?", "#eee", "#333"))

        with st.expander(
            f"{'🥇' if results.index(r)==0 else '🥈' if results.index(r)==1 else '🥉' if results.index(r)==2 else '  '} "
            f"{sig['name']} ({sig['symbol']}) — {res['score']}/100"
        ):
            c1, c2, c3 = st.columns([2, 2, 3])

            with c1:
                st.markdown(f"**Score:** {res['score']}/100")
                st.progress(res['score'] / 100)
                st.markdown(
                    f"<span style='background:{bg};color:{fg};padding:3px 10px;"
                    f"border-radius:6px;font-size:13px;font-weight:600'>{icon}</span>",
                    unsafe_allow_html=True
                )

            with c2:
                chg = sig['price_change_7d']
                st.metric("7d change", f"{chg:+.1f}%")
                st.metric("Dev commits (4w)", sig['github_commits_4w'])

            with c3:
                st.markdown("**Analysis**")
                st.write(ai["summary"])

            col_r, col_o = st.columns(2)
            with col_r:
                st.error(f"Risk: {ai['key_risk']}")
            with col_o:
                st.success(f"Opportunity: {ai['key_opportunity']}")

            if res["red_flags"]:
                flag_labels = {
                    "anonymous_team":      "Anonymous team",
                    "no_audit":            "No smart contract audit",
                    "whale_dumping":       "Whale wallet dumping",
                    "negative_news_spike": "Negative news spike",
                }
                flags_str = " · ".join([f"🚩 {flag_labels.get(f,f)}" for f in res["red_flags"]])
                st.warning(f"Red flags: {flags_str}")

elif run_btn:
    st.warning("Enter at least one coin ID to analyze.")
