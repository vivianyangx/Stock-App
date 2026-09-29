# Investor Research + Options Lab

A mobile-first Streamlit stock research app. Historical charts, indicators and news continue to use Yahoo Finance; the Options Lab uses Alpaca for both the underlying stock quote (SIP) and US option quotes (OPRA by default). The app does not place orders.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run stock_app.py
```

Configure credentials in `.streamlit/secrets.toml` (keep this file out of Git):

```toml
ALPACA_API_KEY = "your-key"
ALPACA_SECRET_KEY = "your-secret"
ALPACA_OPTIONS_FEED = "opra"
```

The free Alpaca options feed is `indicative`, not OPRA. For a Basic-plan test, configure both `ALPACA_OPTIONS_FEED = "indicative"` and `ALPACA_STOCK_FEED = "iex"` in Secrets. These are both Alpaca feeds, but they do not provide consolidated OPRA/SIP coverage. For consolidated data, use `ALPACA_OPTIONS_FEED = "opra"` and `ALPACA_STOCK_FEED = "sip"` with the required account entitlements. Do not commit credentials. Streamlit Community Cloud credentials belong in **App settings → Secrets**.

The Options Lab starts with a plain-English volatility snapshot: reported implied volatility near the stock price, 20-trading-day realized volatility, an approximate one-standard-deviation move to the selected expiration, and an implied-volatility-by-strike chart. The chart uses reported IV only and excludes quotes with a spread wider than 20%; it does not fill missing values with model estimates. IV and realized volatility describe different things, and the estimated move is not a forecast or guaranteed range.

After the volatility view, the scenario tool shows costs and risk. Long option cost uses Ask; a spread uses long Ask minus short Bid. It also shows midpoint reference cost, quote timestamps, and a risk-budget contract estimate. Missing two-sided quotes, zero bids, invalid debits, or stock/option quotes older than two minutes block the cost estimate. Spreads wider than 20% are flagged. Market quotes can change before an order reaches a venue; verify them at your broker and use limit orders.

The app does not continuously maintain an options WebSocket connection; quotes are fetched as snapshots when the scenario renders and refresh with Streamlit reruns. Historical chart prices remain Yahoo sourced and are not used as the Options Lab's current underlying price.

This app is for research and education. Prices are not guaranteed execution prices and the app does not provide personalized investment advice.
