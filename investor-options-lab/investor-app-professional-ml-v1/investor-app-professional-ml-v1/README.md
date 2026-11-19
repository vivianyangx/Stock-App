# Investor Research + Options Lab

A mobile-first Streamlit tracker for stock and ETF research. The beginner-friendly Options Lab leads with plain-English cost, break-even, maximum loss and what-if answers. Quote checks, modeled Greeks, and volatility scenarios remain available under optional advanced sections.

The Overview page also requests recent five-minute bars with pre-market and after-hours data. A fresh extended-hours stock quote is shown as a separate preview and may be used to measure distance from the existing watch zones. Official trend, moving averages and technical signals remain anchored to the completed regular session.

When a fresh extended-hours trade is available, **Next Session Plan** classifies the price as inside, below, between or above the existing watch zones. It provides conditional open scenarios, a regular-session confirmation checklist, reported extended-hours volume and a deliberately capped data-confidence label. It does not convert a thin after-hours trade into an automatic buy or sell signal.

**News Signal** is a transparent first-pass noise filter. It deduplicates similar Yahoo headlines, tags common event types (earnings/guidance, M&A, legal/regulatory, leadership/capital and analyst actions), separates material events from general coverage, and checks whether the observed regular- or extended-session price move agrees with headline direction. The result is one of Confirmed positive, Confirmed negative, Positive/Negative unconfirmed, Mixed/contradicted, Likely noise or Insufficient evidence. This heuristic is not a trained forecast; historical-news walk-forward validation is still required before claiming higher predictive accuracy.

The News page adds a beginner-facing **price scenario** for 1, 5 or 20 sessions. Its width comes from recent annualized volatility scaled by the square root of time. Confirmed positive or negative news applies only a small directional skew; noise or insufficient evidence falls back to a volatility-only range. The page compares this scenario with the technical price map and reported analyst targets, then explains how each reference should be used. These are scenario references—not probability bounds, fair value, a price forecast or a trade instruction—and the news adjustment is intentionally labeled as uncalibrated until historical-news walk-forward testing is completed.

## Professional ML v1

The **Model** tab contains an audited research pipeline rather than an unconditional AI forecast. It builds 36 price, volume, market, Nasdaq and sector-relative factors and evaluates regularized direction and return models at 1-, 5- and 20-session horizons. Training labels that cross into a test year are purged, and each horizon is evaluated on expanding 2021–2025 walk-forward folds.

The current price/volume-only models did **not** demonstrate stable out-of-sample direction skill. Balanced accuracy was approximately 50%, Brier skill was negative, and only one or two of five test years beat the base-rate probability depending on horizon. For that reason, the main Model view displays **Prediction withheld**. Raw probabilities, return estimates, scenario residuals and feature contributions remain collapsed under **Experimental raw output · audit only** so they cannot be confused with a validated signal.

Current headlines are shown as a separate, explicitly uncalibrated overlay. They are not included in the audited probability because a licensed point-in-time historical news archive is not configured. Earnings surprises, SEC-event features and historical options surfaces are also marked `NOT TRAINED`. See `MODEL_CARD.md` for exact results and limitations.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run stock_app.py
```

## Deploy on Streamlit Community Cloud

1. Put `stock_app.py`, `ml_engine.py`, `requirements.txt` and `MODEL_CARD.md` in the root of a public GitHub repository.
2. Keep `model_artifacts/professional_v1.json` inside the `model_artifacts` subfolder.
3. Select the repository and `main` branch in Streamlit Community Cloud.
4. Set **Main file path** to `stock_app.py` and deploy.

Option-chain data is requested only when the user presses **Start an options scenario**. Quotes may be delayed, incomplete, stale, or unavailable. When implied volatility is absent, scenario calculations are explicitly labeled and use recent realized volatility as an estimate.

The app only shows a suggested starting limit price during the regular option session when it has a complete two-sided quote, an acceptable spread and sufficient quote quality. Outside that condition it displays a scenario estimate and explicitly withholds a purchase-price suggestion. Extended-hours stock prices are never presented as live option premiums.

This app is for research and education. It does not connect to a broker, submit orders, predict future prices, or provide personalized investment advice.
