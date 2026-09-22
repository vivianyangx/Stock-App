# Investor Research

A mobile-first Streamlit trade-tracking interface for US-listed securities. It combines delayed Yahoo Finance market data, a clean candlestick chart, transparent technical factors, historical regime evidence, company context and English-language headline polarity. It does not place or recommend trades.

## Run locally

Python 3.11 or 3.12 is recommended:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run stock_app.py
```

Streamlit normally opens `http://localhost:8501` automatically.

## Research workflow

1. Enter a ticker or select one from the watchlist.
2. Choose a holding period and chart range.
3. Enter deployable capital and the maximum percentage at risk on one trade.
4. Review the Price, Trend, Momentum and Risk tabs independently.
5. Use Evidence to compare the current regime with this ticker's historical 5-, 20- and 60-session outcomes.
6. Use Company and News as context, then verify earnings, filings, material news and macro conditions outside this app.

## Methodology

- Technical factors: SMA 20/50/200, RSI 14, MACD 12/26/9, Bollinger Bands, ATR 14 and 20-session average volume.
- Reference map: support, risk threshold and resistance scenarios derived from recent structure and ATR. These are not orders or recommendations.
- Evidence: same-ticker historical analogs show sample size, median forward return, positive-return frequency and a downside-decile outcome for the current price regime.
- Chart: one correctly scaled candlestick panel with a 20-session average. Volume, RSI and forecasts are intentionally kept out of the price panel so they cannot distort its geometry.
- Sentiment: TextBlob scores Yahoo Finance English-language headlines. It cannot determine whether information is material, accurate or already priced in.

## Important limitations

This is a research prototype, not a live quote system, broker, return guarantee or personalized investment recommendation. Historical price models cannot anticipate earnings surprises, policy changes, litigation, capital actions or breaking news. Yahoo Finance data may be delayed or temporarily unavailable. Stops can be exceeded by overnight gaps and fast markets.

## Data accuracy

- The Price tab uses Yahoo Finance daily OHLCV bars and explicitly shows provider, price type and as-of date.
- Download repair is enabled and the app checks missing values, duplicate dates, stale bars and invalid OHLC relationships before displaying analytics.
- Price returns and historical evidence use dividend-adjusted close when available; the candlestick chart continues to show quoted OHLC prices.
- Company metrics such as market capitalization and P/E may refresh on a different schedule from daily prices. They should be checked against company filings or a licensed market-data terminal before professional use.
- Historical evidence uses horizon-spaced observations to reduce overlapping-return inflation and labels small samples as limited.
