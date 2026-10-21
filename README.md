# Global Market Lab V2 — 3-page working prototype

A Streamlit project derived from the user's India Market Dashboard concept. **This is a new starter project; it does not overwrite the uploaded original.**

## Features

- **Market dashboard** — India (illustrative Nifty 50 list), 25 US liquid stocks, 20 ASX stocks, gold futures and ETFs. Top five gainers and losers, market heatmap, CSV export. `st.fragment(run_every="300s")` refreshes visible dashboard automatically every 5 minutes. Vendor prices may update less frequently or be unavailable. **This is not complete-market ranking or a live licensed feed.**
- **Chart lab** — Candle chart, volume, SMA20/50, EMA12/26, Bollinger, VWAP for intraday bars, RSI14, MACD, export.
- **Three-statement + DCF** — editable starting balance sheet and financial drivers; five linked annual income, balance sheet and cash flow projections; mechanically balanced projection (not an independent audit of supplied FY0 figures); unlevered FCFF, WACC and terminal value, WACC/g sensitivities. Amounts in MILLIONS. **Numbers are illustrative, not company-sourced, and the modelling is simplified.** Historical Yahoo statements can be viewed separately for reference.

## Run locally

Python 3.11+ recommended.

```bash
python -m venv .venv
# Windows PowerShell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a NEW GitHub repo such as `global-market-lab-v2`.
2. **Extract** the ZIP, then upload its *contents* into the GitHub repository root preserving folders: `app.py`, `core/`, `pages/`, `.streamlit/`, `requirements.txt`. Do **not** upload the ZIP itself as the project entry point.
3. Go to https://share.streamlit.io, create an app from that repository and choose `app.py` as entry point.
4. After each GitHub push the application redeploys. Public visitors can access its public URL, within free-tier limitations.

## Data source and usage

The current prototype uses **Yahoo/yfinance** (unofficial personal/research use). A 5-minute UI refresh is not proof of true 5-minute exchange price freshness. Intraday data is best effort and Yahoo may throttle bulk ticker downloads. Display timestamps indicate last source bar. Market and futures calendars differ. Gold futures `GC=F` are **not** gold spot price; `GLD` and `IAU` are US ETFs and `GOLD.AX` is an ASX product — do not compare their prices directly. Gold rankings compare returns across distinct instruments.

**Before public/commercial distribution of live data, obtain appropriate provider + exchange display/redistribution licensing.** Avoid using Yahoo data commercially. Planned next step: add a provider adapter (`MarketDataProvider`) to support EODHD for licensed EOD/fundamentals and a separately licensed intraday feed where available; validate India market timing and exchange entitlements with provider.

## Future enhancements

- True constituents API instead of static lists; index-wide Top 5.
- Market status/time zones/holiday calendar, delayed-data badges, redistributable quote entitlements.
- Corporate filings and audit mapping to canonical historical financial statements, 3-year actuals and 5-year forecasts, sector-specific models (banks/REITs/miners).
- Scenario table, bull/base/bear, Monte Carlo, relative valuation, price vs intrinsic value with market cap, fully diluted shares, currency translation, risk-free yield/ERP/beta for WACC.
- Licensed production data, authentication, monitoring, background scheduled ingestion and durable cache/DB.

## Testing

```bash
pip install pytest
pytest -q
```

Included tests cover 3-statement balance, DCF linkage, monotonic WACC and intraday vs previous-close calculation. They do not verify that Yahoo's live API returns data consistently.
