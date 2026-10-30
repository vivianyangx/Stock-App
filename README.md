# Investor Research + Options Lab

A mobile-first Streamlit tracker for stock and ETF research. The beginner-friendly Options Lab leads with plain-English cost, break-even, maximum loss and what-if answers. Quote checks, modeled Greeks, and volatility scenarios remain available under optional advanced sections.

The Overview page also requests recent five-minute bars with pre-market and after-hours data. A fresh extended-hours stock quote is shown as a separate preview and may be used to measure distance from the existing watch zones. Official trend, moving averages and technical signals remain anchored to the completed regular session.

When a fresh extended-hours trade is available, **Next Session Plan** classifies the price as inside, below, between or above the existing watch zones. It provides conditional open scenarios, a regular-session confirmation checklist, reported extended-hours volume and a deliberately capped data-confidence label. It does not convert a thin after-hours trade into an automatic buy or sell signal.

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

The app only shows a suggested starting limit price during the regular option session when it has a complete two-sided quote, an acceptable spread and sufficient quote quality. Outside that condition it displays a scenario estimate and explicitly withholds a purchase-price suggestion. Extended-hours stock prices are never presented as live option premiums.

This app is for research and education. It does not connect to a broker, submit orders, predict future prices, or provide personalized investment advice.
