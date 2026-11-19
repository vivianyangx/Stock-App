"""Point-in-time feature engineering and portable inference for Professional ML v1.

The deployed app uses a JSON artifact rather than a pickled estimator so model
behavior is inspectable and independent of the scikit-learn runtime version.
Training lives in ``train_professional_model.py``.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


HORIZONS = (1, 5, 20)

FEATURES = [
    "ret_1", "ret_5", "ret_10", "ret_20",
    "dist_ma20", "dist_ma50", "dist_ma200",
    "vol_10", "vol_20", "atr_pct", "gap_1", "range_pct",
    "rel_volume", "rsi_centered", "drawdown_20", "drawdown_60",
    "spy_ret_5", "spy_ret_20", "spy_vol_20",
    "spy_dist_ma20", "spy_dist_ma200", "spy_drawdown_60", "market_bear",
    "excess_spy_5", "excess_spy_20",
    "qqq_ret_5", "qqq_ret_20", "qqq_dist_ma200",
    "sector_ret_5", "sector_ret_20", "sector_dist_ma200",
    "excess_sector_5", "excess_sector_20", "beta_60",
    "vol_ratio_market", "momentum_in_bear",
]

FEATURE_LABELS = {
    "ret_1": "1-day momentum", "ret_5": "1-week momentum",
    "ret_10": "2-week momentum", "ret_20": "1-month momentum",
    "dist_ma20": "distance from 20-day average",
    "dist_ma50": "distance from 50-day average",
    "dist_ma200": "distance from 200-day average",
    "vol_10": "10-day realized volatility", "vol_20": "20-day realized volatility",
    "atr_pct": "daily trading range", "gap_1": "latest opening gap",
    "range_pct": "intraday range", "rel_volume": "relative volume",
    "rsi_centered": "RSI momentum", "drawdown_20": "distance from 20-day high",
    "drawdown_60": "distance from 60-day high",
    "spy_ret_5": "S&P 500 weekly trend", "spy_ret_20": "S&P 500 monthly trend",
    "spy_vol_20": "market volatility", "excess_spy_5": "weekly strength vs S&P 500",
    "spy_dist_ma20": "S&P 500 distance from 20-day average",
    "spy_dist_ma200": "S&P 500 distance from 200-day average",
    "spy_drawdown_60": "S&P 500 drawdown", "market_bear": "weak-market regime",
    "excess_spy_20": "monthly strength vs S&P 500",
    "qqq_ret_5": "Nasdaq weekly trend", "qqq_ret_20": "Nasdaq monthly trend",
    "qqq_dist_ma200": "Nasdaq long-term trend",
    "sector_ret_5": "sector weekly trend", "sector_ret_20": "sector monthly trend",
    "sector_dist_ma200": "sector long-term trend",
    "excess_sector_5": "weekly strength vs sector",
    "excess_sector_20": "monthly strength vs sector", "beta_60": "60-day market beta",
    "vol_ratio_market": "volatility vs market", "momentum_in_bear": "momentum during weak markets",
}

SECTOR_BY_TICKER = {
    "AAPL": "XLK", "MSFT": "XLK", "NVDA": "XLK", "AVGO": "XLK",
    "AMD": "XLK", "META": "XLC", "GOOGL": "XLC", "NFLX": "XLC",
    "AMZN": "XLY", "TSLA": "XLY", "HD": "XLY", "COST": "XLP",
    "PG": "XLP", "JPM": "XLF", "XOM": "XLE", "UNH": "XLV",
    "JNJ": "XLV",
}

SECTOR_NAME_MAP = {
    "technology": "XLK", "communication services": "XLC",
    "consumer cyclical": "XLY", "consumer defensive": "XLP",
    "financial services": "XLF", "financial": "XLF", "energy": "XLE",
    "healthcare": "XLV", "industrials": "XLI", "basic materials": "XLB",
    "real estate": "XLRE", "utilities": "XLU",
}


def sector_symbol_for(ticker: str, sector_name: str | None = None) -> str:
    ticker = ticker.upper().strip()
    if ticker in {"SPY", "QQQ", "IWM", "DIA"}:
        return "SPY"
    if ticker.startswith("XL") and len(ticker) <= 4:
        return ticker
    if ticker in SECTOR_BY_TICKER:
        return SECTOR_BY_TICKER[ticker]
    return SECTOR_NAME_MAP.get(str(sector_name or "").lower(), "SPY")


def _clean_frame(frame: pd.DataFrame) -> pd.DataFrame:
    work = frame.copy()
    if isinstance(work.columns, pd.MultiIndex):
        work.columns = work.columns.get_level_values(0)
    required = ["Open", "High", "Low", "Close", "Volume"]
    missing = [column for column in required if column not in work]
    if missing:
        raise ValueError(f"Missing OHLCV columns: {', '.join(missing)}")
    work.index = pd.DatetimeIndex(work.index).tz_localize(None).normalize()
    work = work.loc[~work.index.duplicated(keep="last")].sort_index()
    for column in required:
        work[column] = pd.to_numeric(work[column], errors="coerce")
    if "ReturnClose" in work:
        work["ModelClose"] = pd.to_numeric(work["ReturnClose"], errors="coerce")
    elif "Adj Close" in work:
        work["ModelClose"] = pd.to_numeric(work["Adj Close"], errors="coerce")
    else:
        work["ModelClose"] = work["Close"]
    return work.dropna(subset=["Open", "High", "Low", "Close", "ModelClose"])


def _base_features(frame: pd.DataFrame) -> pd.DataFrame:
    work = _clean_frame(frame)
    close = work["ModelClose"]
    raw_close = work["Close"]
    returns = close.pct_change()
    out = pd.DataFrame(index=work.index)
    for sessions in (1, 5, 10, 20):
        out[f"ret_{sessions}"] = close.pct_change(sessions)
    for sessions in (20, 50, 200):
        out[f"dist_ma{sessions}"] = close / close.rolling(sessions).mean() - 1
    out["vol_10"] = returns.rolling(10).std() * math.sqrt(252)
    out["vol_20"] = returns.rolling(20).std() * math.sqrt(252)
    previous = raw_close.shift(1)
    true_range = pd.concat([
        work["High"] - work["Low"],
        (work["High"] - previous).abs(),
        (work["Low"] - previous).abs(),
    ], axis=1).max(axis=1)
    out["atr_pct"] = true_range.ewm(alpha=1 / 14, adjust=False).mean() / raw_close
    out["gap_1"] = work["Open"] / previous - 1
    out["range_pct"] = (work["High"] - work["Low"]) / raw_close
    volume_average = work["Volume"].rolling(20).mean().replace(0, np.nan)
    out["rel_volume"] = np.log1p(work["Volume"] / volume_average).replace([np.inf, -np.inf], np.nan)
    delta = close.diff()
    gain = delta.clip(lower=0).ewm(alpha=1 / 14, adjust=False).mean()
    loss = (-delta.clip(upper=0)).ewm(alpha=1 / 14, adjust=False).mean()
    rsi = 100 - 100 / (1 + gain / loss.replace(0, np.nan))
    out["rsi_centered"] = (rsi - 50) / 50
    out["drawdown_20"] = close / close.rolling(20).max() - 1
    out["drawdown_60"] = close / close.rolling(60).max() - 1
    out["daily_return"] = returns
    out["model_close"] = close
    return out


def build_feature_frame(
    ticker_frame: pd.DataFrame,
    spy_frame: pd.DataFrame,
    qqq_frame: pd.DataFrame,
    sector_frame: pd.DataFrame,
) -> pd.DataFrame:
    stock = _base_features(ticker_frame)
    spy = _base_features(spy_frame).reindex(stock.index).ffill()
    qqq = _base_features(qqq_frame).reindex(stock.index).ffill()
    sector = _base_features(sector_frame).reindex(stock.index).ffill()

    out = stock.copy()
    out["spy_ret_5"] = spy["ret_5"]
    out["spy_ret_20"] = spy["ret_20"]
    out["spy_vol_20"] = spy["vol_20"]
    out["spy_dist_ma20"] = spy["dist_ma20"]
    out["spy_dist_ma200"] = spy["dist_ma200"]
    out["spy_drawdown_60"] = spy["drawdown_60"]
    out["market_bear"] = (spy["dist_ma200"] < 0).astype(float)
    out["excess_spy_5"] = out["ret_5"] - out["spy_ret_5"]
    out["excess_spy_20"] = out["ret_20"] - out["spy_ret_20"]
    out["qqq_ret_5"] = qqq["ret_5"]
    out["qqq_ret_20"] = qqq["ret_20"]
    out["qqq_dist_ma200"] = qqq["dist_ma200"]
    out["sector_ret_5"] = sector["ret_5"]
    out["sector_ret_20"] = sector["ret_20"]
    out["sector_dist_ma200"] = sector["dist_ma200"]
    out["excess_sector_5"] = out["ret_5"] - out["sector_ret_5"]
    out["excess_sector_20"] = out["ret_20"] - out["sector_ret_20"]
    covariance = out["daily_return"].rolling(60).cov(spy["daily_return"])
    market_variance = spy["daily_return"].rolling(60).var().replace(0, np.nan)
    out["beta_60"] = covariance / market_variance
    out["vol_ratio_market"] = out["vol_20"] / spy["vol_20"].replace(0, np.nan)
    out["momentum_in_bear"] = out["ret_20"] * out["market_bear"]
    return out.replace([np.inf, -np.inf], np.nan)


def load_artifact(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        artifact = json.load(handle)
    if artifact.get("features") != FEATURES:
        raise ValueError("Model feature schema does not match this app version")
    return artifact


def _sigmoid(value: float) -> float:
    value = float(np.clip(value, -35, 35))
    return 1.0 / (1.0 + math.exp(-value))


def _transform(row: pd.Series, model: dict[str, Any]) -> np.ndarray:
    values = row[FEATURES].to_numpy(dtype=float)
    lower = np.asarray(model["clip_lower"], dtype=float)
    upper = np.asarray(model["clip_upper"], dtype=float)
    mean = np.asarray(model["scaler_mean"], dtype=float)
    scale = np.asarray(model["scaler_scale"], dtype=float)
    return (np.clip(values, lower, upper) - mean) / np.where(scale == 0, 1.0, scale)


def predict_latest(
    artifact: dict[str, Any],
    ticker_frame: pd.DataFrame,
    spy_frame: pd.DataFrame,
    qqq_frame: pd.DataFrame,
    sector_frame: pd.DataFrame,
    spot: float,
) -> dict[int, dict[str, Any]]:
    features = build_feature_frame(ticker_frame, spy_frame, qqq_frame, sector_frame)
    usable = features.dropna(subset=FEATURES)
    if usable.empty:
        raise ValueError("Not enough aligned history to calculate model features")
    row = usable.iloc[-1]
    feature_date = pd.Timestamp(usable.index[-1]).strftime("%b %d, %Y")
    predictions: dict[int, dict[str, Any]] = {}
    for horizon in HORIZONS:
        model = artifact["horizons"][str(horizon)]
        transformed = _transform(row, model)
        logit = float(np.dot(np.asarray(model["classifier_coef"]), transformed) +
                      model["classifier_intercept"])
        probability = _sigmoid(logit)
        expected_return = float(np.dot(np.asarray(model["regressor_coef"]), transformed) +
                                model["regressor_intercept"])
        lower_return = expected_return + float(model["oos_residual_q10"])
        upper_return = expected_return + float(model["oos_residual_q90"])
        contributions = np.asarray(model["classifier_coef"]) * transformed
        order = np.argsort(np.abs(contributions))[::-1]
        drivers = [{
            "feature": FEATURES[index],
            "label": FEATURE_LABELS.get(FEATURES[index], FEATURES[index]),
            "contribution": float(contributions[index]),
            "direction": "supportive" if contributions[index] > 0 else "caution",
        } for index in order[:6]]
        outlier_count = int((np.abs(transformed) > 3).sum())
        predictions[horizon] = {
            "up_probability": probability,
            "expected_return": expected_return,
            "range_low": max(0.01, spot * (1 + lower_return)),
            "range_high": max(0.01, spot * (1 + upper_return)),
            "feature_date": feature_date,
            "drivers": drivers,
            "outlier_features": outlier_count,
            "metrics": model["walk_forward"],
            "quality": model["quality"],
        }
    return predictions

