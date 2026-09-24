# Investor Research + Options Lab

A mobile-first Streamlit tracker for stock and ETF research. The beginner-friendly Options Lab leads with plain-English cost, break-even, maximum loss and what-if answers. Quote checks, modeled Greeks, and volatility scenarios remain available under optional advanced sections.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run stock_app.py
```

## Deploy on Streamlit Community Cloud

1. Put `stock_app.py` and `requirements.txt` in the root of a public GitHub repository.
2. Select the repository and `main` branch in Streamlit Community Cloud.
3. Set **Main file path** to `stock_app.py` and deploy.

Option-chain data is requested only when the user presses **Start an options scenario**. Quotes may be delayed, incomplete, stale, or unavailable. When implied volatility is absent, scenario calculations are explicitly labeled and use recent realized volatility as an estimate.

This app is for research and education. It does not connect to a broker, submit orders, predict future prices, or provide personalized investment advice.
