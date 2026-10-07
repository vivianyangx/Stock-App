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

The Volatility tab follows a short research flow: (1) compare recent stock volatility with the approximate move priced by options through the selected expiration; (2) choose Call or Put, expiration, strike and a hypothetical stock price at expiration; (3) review Ask-based contract cost and the possible result under that assumption. The expiration list requests active contracts up to one year ahead (Alpaca otherwise defaults to near-term expirations). The implied-volatility-by-strike chart and quote/Greek details are collapsed by default. Implied and realized volatility describe different things, and the estimated move is not a forecast or guaranteed range.

The Call/Put selector filters the volatility study; it is not a direction recommendation. Users choose a listed strike and enter a hypothetical stock price at expiration. The long-option example uses Ask × 100 for its conservative purchase-cost estimate and midpoint only as a reference. Its expiration result assumes one long contract held through expiration, excludes fees, and does not predict the entered stock price. Missing or invalid two-sided quotes, zero bids, or stock/option quotes older than two minutes block the current cost and profit/loss estimate. Spreads wider than 20% and low volume/open interest are flagged. Quotes are estimates, not guaranteed execution prices.

The plain-English volatility and scenario notes are deterministic explanations of the displayed values, not a connected generative AI system. They do not provide personalized buy/sell recommendations.

The app does not continuously maintain an options WebSocket connection; quotes are fetched as snapshots when the scenario renders and refresh with Streamlit reruns. Historical chart prices remain Yahoo sourced and are not used as the Options Lab's current underlying price.

The main navigation keeps **Stock Prediction** first, **Options** as the same ticker's follow-on research, and secondary **Signals**, **Risk**, and **Research** sections under **More**. Stock ranges are technical watch zones derived from historical price structure and volatility, not guaranteed predictions or orders.

This app is for research and education. Prices are not guaranteed execution prices and the app does not provide personalized investment advice.
