# Professional Data Roadmap

Professional ML v1 deliberately separates connected inputs from factors that
have not yet been trained.  A green UI badge means data was available to the
current artifact; it does not mean the factor is predictive.

## Connected in v1

- Daily adjusted OHLCV for a selected liquid-US universe.
- SPY and QQQ market context.
- Sector ETF relative strength.
- 36 price, volume, volatility, drawdown, beta and regime features.

The research prototype was trained from Yahoo-sourced history through the date
shown in the model artifact.  Yahoo is not an institutional point-in-time feed
and is not an appropriate redistribution source for a production public app.

## Recommended next connection: historical news

For an individual research prototype, Alpaca Historical News provides symbol
tags and creation timestamps.  For institutional research, use a licensed
archive such as LSEG News Analytics or RavenPack with relevance, novelty and
event metadata.  Live headlines alone are insufficient: the model needs the
historical archive that would actually have been available at each prediction
timestamp.

Store credentials in Streamlit Secrets or environment variables, never inside
`stock_app.py`, GitHub, a ZIP archive or chat.  Proposed secret names:

```toml
ALPACA_API_KEY_ID = "..."
ALPACA_API_SECRET_KEY = "..."
FRED_API_KEY = "..."
```

## Later connections

1. Point-in-time earnings estimates, actual results and guidance revisions.
2. SEC 8-K, 10-Q, 10-K and Form 4 event timestamps.
3. Licensed historical OPRA option quotes, implied volatility, skew and open interest.
4. ALFRED macro vintages rather than subsequently revised macro observations.
5. FINRA/exchange short-interest snapshots; do not substitute daily short-sale volume.

## Acceptance gate for every new factor

- Timestamp and join the data as it existed at prediction time.
- Add one factor family at a time.
- Re-run purged expanding-year walk-forward folds.
- Compare Brier score, balanced accuracy, return correlation and interval coverage.
- Keep a factor only when improvement persists across multiple unseen periods.
- Run a final untouched confirmation period before changing the production label.

Do not promote a model merely because one backtest, ticker or market regime looks
good.  Public redistribution also requires the relevant vendor license.

