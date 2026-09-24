# Investor Research + Options Lab

A mobile-first Streamlit tracker for stock and ETF research. The Options Lab adds delayed option-chain screening, quote-quality checks, modeled Greeks, defined-risk strategy comparisons, and price/time/volatility scenarios.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run stock_app.py
```

## Deploy on Streamlit Community Cloud

1. Put `stock_app.py` and `requirements.txt` in the root of a public GitHub repository.
2. Select the repository and `main` branch in Streamlit Community Cloud.
3. Set **Main file path** to `stock_app.py` and deploy.

Option-chain data is requested only when the user presses **Load live option chain**. Quotes may be delayed, incomplete, stale, or unavailable. When implied volatility is absent, scenario calculations are explicitly labeled and use recent realized volatility as an estimate.

This app is for research and education. It does not connect to a broker, submit orders, predict future prices, or provide personalized investment advice.
