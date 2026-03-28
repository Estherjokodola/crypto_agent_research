# 📊 Crypto Research Agent

A short-term crypto trading research tool that scores and analyzes crypto projects using live market data, developer activity, and sentiment signals — with plain-English verdicts to help you make faster, smarter decisions.

---

## 🚀 Live Demo

[**→ Open the app**](https://your-username-crypto-agent-dashboard.streamlit.app)

---

## 🧠 What it does

- Fetches live data from CoinGecko (price, volume, market cap, dev activity, community)
- Scores every project from **0–100** across 7 weighted signals
- Detects **red flags** (anonymous team, no audit, whale dumping, negative news)
- Generates a plain-English **Buy / Watch / Avoid** verdict with reasoning
- Compares multiple coins side by side in a ranked table
- Runs automated alerts on a watchlist — only fires when something is worth acting on

---

## 📸 Screenshots

> Add screenshots here after deployment

---

## 🧩 How the scoring works

Every coin is scored across 7 signals, grouped into 3 categories:

| Category | Signal | Weight |
|---|---|---|
| Momentum | Price trend (7d) | 20% |
| Momentum | Volume spike | 15% |
| Fundamentals | Developer activity | 15% |
| Fundamentals | Tokenomics | 10% |
| Fundamentals | Liquidity | 10% |
| Sentiment | Social sentiment | 15% |
| Sentiment | News sentiment | 15% |

**Verdict thresholds:**
- ✅ **Buy** — score 70+ with no red flags
- 👀 **Watch** — score 45–69
- 🚫 **Avoid** — score below 45, or any red flag triggered

**Red flags override everything.** A coin scoring 90/100 still gets AVOID if it has an anonymous team or no smart contract audit.

---

## 🗂️ Project structure
```
crypto-agent/
├── pages/
│   └── compare.py       # multi-coin comparison page
├── .env                 # API keys (never commit this)
├── config.py            # scoring weights + thresholds
├── data_fetcher.py      # CoinGecko API integration
├── scorer.py            # scoring formula
├── ai_analyzer.py       # rule-based reasoning engine
├── dashboard.py         # main Streamlit app
├── alerts.py            # automated watchlist alerts
├── main.py              # terminal version
└── requirements.txt
```

---

## ⚙️ Run locally

**1. Clone the repo**
```bash
git clone https://github.com/YOUR_USERNAME/crypto-agent.git
cd crypto-agent
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac / Linux
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Set up your environment**

Create a `.env` file in the root folder:
```
ANTHROPIC_API_KEY=your_key_here
```
> The tool works without an API key — the rule-based analyzer runs fully offline.

**5. Run the dashboard**
```bash
streamlit run dashboard.py
```

**6. Run the terminal version**
```bash
python main.py
```

**7. Run alerts**
```bash
python alerts.py --once        # single check
python alerts.py               # runs every 60 minutes
python alerts.py 30            # runs every 30 minutes
```

---

## 📡 Data sources

| Source | What it provides | Cost |
|---|---|---|
| [CoinGecko API](https://coingecko.com) | Price, volume, market cap, dev data, community | Free |
| Rule-based engine | Tokenomics scoring, sentiment, red flag detection | Free |

No paid API required to run this tool.

---

## 🗺️ Roadmap

- [ ] Real news sentiment via RSS scraping
- [ ] Twitter/X sentiment via API
- [ ] Email alerts via SMTP
- [ ] Portfolio tracker — monitor coins you hold
- [ ] Backtesting — validate scoring model against historical data
- [ ] Fine-tuned ML model to replace rule-based analyzer

---

## 🛠️ Built with

- [Python](https://python.org)
- [Streamlit](https://streamlit.io) — dashboard UI
- [CoinGecko API](https://coingecko.com/en/api) — market data
- [Requests](https://requests.readthedocs.io) — HTTP client

---

## 👤 Author

Built by **[Your Name]**
- GitHub: [@your_username](https://github.com/your_username)
- LinkedIn: [your profile](https://linkedin.com/in/your_username)

---

## ⚠️ Disclaimer

This tool is for **research and educational purposes only**. It is not financial advice. Always do your own research before making any investment decisions. Crypto markets are highly volatile and unpredictable.

---

## 📄 License

MIT License — free to use, modify, and distribute.
