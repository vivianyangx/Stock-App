# Professional ML v1 — Model Card

Generated: 2026-11-19T05:01:30.007553+00:00

## Intended use

Estimate 1-, 5- and 20-session direction probabilities and return scenarios for research. 
The models are not trade instructions, fair-value models or guarantees.

## Design

- Pooled liquid US-stock and ETF daily OHLCV data.
- Price, volume, market, Nasdaq and sector-relative features.
- Regularized logistic direction model plus ridge expected-return model.
- Expanding-year 2021–2025 walk-forward tests.
- Forward labels crossing a test boundary are purged from training.
- 1st/99th-percentile feature clipping is learned on each training fold.
- Scenario bounds use 10th/90th percentile out-of-sample residuals.

## Walk-forward results

| Horizon | Observations | Accuracy | Balanced accuracy | Brier skill | Return correlation | Positive folds | Quality |
|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | 30,120 | 51.9% | 50.4% | -1.16% | 0.004 | 0/5 | No stable edge demonstrated |
| 5 | 30,120 | 54.2% | 50.5% | -2.90% | -0.013 | 1/5 | No stable edge demonstrated |
| 20 | 30,120 | 55.1% | 49.7% | -12.81% | -0.041 | 1/5 | No stable edge demonstrated |

## Important limitations

- The training universe is selected and therefore has survivorship/selection bias.
- Daily bars do not reconstruct intraday execution or bid/ask spreads.
- Earnings, point-in-time fundamentals, options and historical news are not in v1.
- Current News Signal is displayed as a separate uncalibrated overlay and is not included in backtested probability.
- Model quality can decay as market structure changes; retraining and drift monitoring are required.
- A public app requires appropriate data redistribution licenses.

## Fold audit file

See `walk_forward_folds.csv` and `walk_forward_predictions.csv` in this directory.
