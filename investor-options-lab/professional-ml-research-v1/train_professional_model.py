"""Train and evaluate the app's inspectable Professional ML v1 models.

The script uses expanding-year walk-forward folds and purges observations whose
forward-return label crosses into the test period.  It produces a portable JSON
artifact consumed by ``outputs/ml_engine.py`` plus audit CSVs and a Markdown
model card.
"""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    brier_score_loss,
    log_loss,
    mean_absolute_error,
    roc_auc_score,
)
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "outputs"))
from ml_engine import FEATURES, HORIZONS, build_feature_frame, sector_symbol_for  # noqa: E402


CACHE_PATH = ROOT / "ml_results" / "ml_price_cache.pkl"
RESULTS_DIR = ROOT / "ml_results"
ARTIFACT_PATH = ROOT / "outputs" / "model_artifacts" / "professional_v1.json"
TEST_YEARS = range(2021, 2026)
MIN_TRAIN_DATE = pd.Timestamp("2017-01-01")
TRAINING_UNIVERSE = [
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO",
    "JPM", "XOM", "UNH", "JNJ", "PG", "COST", "HD", "AMD", "NFLX",
    "SPY", "QQQ", "IWM", "DIA", "XLK", "XLF", "XLE",
]


def prepare_dataset(history: dict[str, pd.DataFrame], horizon: int) -> pd.DataFrame:
    rows = []
    spy = history["SPY"]
    qqq = history["QQQ"]
    # Context-only sector ETFs and leveraged TQQQ are not pooled as targets.
    # The deployed model can still score them, but must label that use as extrapolative.
    for ticker in TRAINING_UNIVERSE:
        sector_symbol = sector_symbol_for(ticker)
        sector = history.get(sector_symbol, spy)
        features = build_feature_frame(history[ticker], spy, qqq, sector)
        features["target_return"] = features["model_close"].shift(-horizon) / features["model_close"] - 1
        features["target_up"] = (features["target_return"] > 0).astype(float)
        feature_index = pd.Series(features.index, index=features.index)
        features["label_date"] = feature_index.shift(-horizon)
        features["ticker"] = ticker
        features["date"] = features.index
        rows.append(features.reset_index(drop=True))
    dataset = pd.concat(rows, ignore_index=True)
    dataset = dataset.dropna(subset=FEATURES + ["target_return", "target_up", "label_date"])
    dataset = dataset.loc[dataset["date"] >= MIN_TRAIN_DATE].copy()
    dataset["target_up"] = dataset["target_up"].astype(int)
    return dataset.sort_values(["date", "ticker"]).reset_index(drop=True)


def fit_models(train: pd.DataFrame) -> dict:
    x = train[FEATURES].to_numpy(dtype=float)
    y_class = train["target_up"].to_numpy(dtype=int)
    y_return = train["target_return"].to_numpy(dtype=float)
    lower = np.nanquantile(x, 0.01, axis=0)
    upper = np.nanquantile(x, 0.99, axis=0)
    x_clipped = np.clip(x, lower, upper)
    scaler = StandardScaler().fit(x_clipped)
    x_scaled = scaler.transform(x_clipped)
    classifier = LogisticRegression(C=0.20, max_iter=1500, solver="lbfgs")
    classifier.fit(x_scaled, y_class)
    regression_target = np.clip(
        y_return,
        np.quantile(y_return, 0.01),
        np.quantile(y_return, 0.99),
    )
    regressor = Ridge(alpha=50.0)
    regressor.fit(x_scaled, regression_target)
    return {
        "lower": lower, "upper": upper, "scaler": scaler,
        "classifier": classifier, "regressor": regressor,
    }


def predict(model: dict, frame: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    x = frame[FEATURES].to_numpy(dtype=float)
    x = np.clip(x, model["lower"], model["upper"])
    x = model["scaler"].transform(x)
    return (
        model["classifier"].predict_proba(x)[:, 1],
        model["regressor"].predict(x),
    )


def evaluate(test: pd.DataFrame, probability: np.ndarray,
             expected_return: np.ndarray, baseline_probability: float,
             baseline_return: float) -> dict:
    actual_up = test["target_up"].to_numpy(dtype=int)
    actual_return = test["target_return"].to_numpy(dtype=float)
    baseline_probabilities = np.full(len(test), baseline_probability)
    baseline_returns = np.full(len(test), baseline_return)
    brier = brier_score_loss(actual_up, probability)
    baseline_brier = brier_score_loss(actual_up, baseline_probabilities)
    mae = mean_absolute_error(actual_return, expected_return)
    baseline_mae = mean_absolute_error(actual_return, baseline_returns)
    correlation = float(np.corrcoef(expected_return, actual_return)[0, 1])
    return {
        "observations": int(len(test)),
        "up_rate": float(actual_up.mean()),
        "accuracy": float(accuracy_score(actual_up, probability >= 0.5)),
        "balanced_accuracy": float(balanced_accuracy_score(actual_up, probability >= 0.5)),
        "brier": float(brier), "baseline_brier": float(baseline_brier),
        "brier_skill": float(1 - brier / baseline_brier) if baseline_brier else 0.0,
        "log_loss": float(log_loss(actual_up, probability, labels=[0, 1])),
        "roc_auc": float(roc_auc_score(actual_up, probability)),
        "return_mae": float(mae), "baseline_return_mae": float(baseline_mae),
        "mae_skill": float(1 - mae / baseline_mae) if baseline_mae else 0.0,
        "return_correlation": correlation if np.isfinite(correlation) else 0.0,
    }


def quality_label(metrics: dict, positive_folds: int) -> str:
    if metrics["brier_skill"] > 0.01 and metrics["return_correlation"] > 0.04 and positive_folds >= 4:
        return "Moderate historical edge"
    if metrics["brier_skill"] > 0 and metrics["return_correlation"] > 0 and positive_folds >= 3:
        return "Limited historical edge"
    return "No stable edge demonstrated"


def train_horizon(dataset: pd.DataFrame, horizon: int) -> tuple[dict, list[dict], pd.DataFrame]:
    fold_rows: list[dict] = []
    prediction_rows = []
    for test_year in TEST_YEARS:
        test_start = pd.Timestamp(f"{test_year}-01-01")
        test_end = pd.Timestamp(f"{test_year}-12-31")
        train = dataset.loc[(dataset["date"] < test_start) &
                            (dataset["label_date"] < test_start)].copy()
        test = dataset.loc[dataset["date"].between(test_start, test_end)].copy()
        if len(train) < 5_000 or test.empty:
            continue
        model = fit_models(train)
        probability, expected_return = predict(model, test)
        metrics = evaluate(
            test, probability, expected_return,
            float(train["target_up"].mean()), float(train["target_return"].mean()),
        )
        fold_rows.append({"horizon": horizon, "test_year": test_year, **metrics})
        prediction_rows.append(pd.DataFrame({
            "horizon": horizon, "test_year": test_year,
            "date": test["date"].to_numpy(), "ticker": test["ticker"].to_numpy(),
            "actual_up": test["target_up"].to_numpy(),
            "actual_return": test["target_return"].to_numpy(),
            "up_probability": probability, "expected_return": expected_return,
        }))

    predictions = pd.concat(prediction_rows, ignore_index=True)
    aggregate = evaluate(
        predictions.rename(columns={"actual_up": "target_up", "actual_return": "target_return"}),
        predictions["up_probability"].to_numpy(),
        predictions["expected_return"].to_numpy(),
        float(predictions["actual_up"].mean()), float(predictions["actual_return"].mean()),
    )
    positive_folds = sum(row["brier_skill"] > 0 for row in fold_rows)
    aggregate["positive_brier_skill_folds"] = int(positive_folds)
    aggregate["folds"] = len(fold_rows)

    final_model = fit_models(dataset)
    final_probability, final_expected = predict(final_model, dataset)
    # OOS residuals provide a more honest scenario range than in-sample residuals.
    oos_residual = predictions["actual_return"] - predictions["expected_return"]
    artifact = {
        "classifier_coef": final_model["classifier"].coef_[0].tolist(),
        "classifier_intercept": float(final_model["classifier"].intercept_[0]),
        "regressor_coef": final_model["regressor"].coef_.tolist(),
        "regressor_intercept": float(final_model["regressor"].intercept_),
        "clip_lower": final_model["lower"].tolist(),
        "clip_upper": final_model["upper"].tolist(),
        "scaler_mean": final_model["scaler"].mean_.tolist(),
        "scaler_scale": final_model["scaler"].scale_.tolist(),
        "oos_residual_q10": float(oos_residual.quantile(0.10)),
        "oos_residual_q90": float(oos_residual.quantile(0.90)),
        "training_observations": int(len(dataset)),
        "training_up_rate": float(dataset["target_up"].mean()),
        "in_sample_probability_mean": float(final_probability.mean()),
        "in_sample_return_mean": float(final_expected.mean()),
        "walk_forward": aggregate,
        "quality": quality_label(aggregate, positive_folds),
    }
    return artifact, fold_rows, predictions


def write_model_card(artifact: dict, folds: pd.DataFrame) -> None:
    lines = [
        "# Professional ML v1 — Model Card", "",
        f"Generated: {artifact['created_at_utc']}", "",
        "## Intended use", "",
        "Estimate 1-, 5- and 20-session direction probabilities and return scenarios for research. ",
        "The models are not trade instructions, fair-value models or guarantees.", "",
        "## Design", "",
        "- Pooled liquid US-stock and ETF daily OHLCV data.",
        "- Price, volume, market, Nasdaq and sector-relative features.",
        "- Regularized logistic direction model plus ridge expected-return model.",
        "- Expanding-year 2021–2025 walk-forward tests.",
        "- Forward labels crossing a test boundary are purged from training.",
        "- 1st/99th-percentile feature clipping is learned on each training fold.",
        "- Scenario bounds use 10th/90th percentile out-of-sample residuals.", "",
        "## Walk-forward results", "",
        "| Horizon | Observations | Accuracy | Balanced accuracy | Brier skill | Return correlation | Positive folds | Quality |",
        "|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for horizon in HORIZONS:
        model = artifact["horizons"][str(horizon)]
        metrics = model["walk_forward"]
        lines.append(
            f"| {horizon} | {metrics['observations']:,} | {metrics['accuracy']:.1%} | "
            f"{metrics['balanced_accuracy']:.1%} | {metrics['brier_skill']:.2%} | "
            f"{metrics['return_correlation']:.3f} | "
            f"{metrics['positive_brier_skill_folds']}/{metrics['folds']} | {model['quality']} |"
        )
    lines.extend([
        "", "## Important limitations", "",
        "- The training universe is selected and therefore has survivorship/selection bias.",
        "- Daily bars do not reconstruct intraday execution or bid/ask spreads.",
        "- Earnings, point-in-time fundamentals, options and historical news are not in v1.",
        "- Current News Signal is displayed as a separate uncalibrated overlay and is not included in backtested probability.",
        "- Model quality can decay as market structure changes; retraining and drift monitoring are required.",
        "- A public app requires appropriate data redistribution licenses.", "",
        "## Fold audit file", "",
        "See `walk_forward_folds.csv` and `walk_forward_predictions.csv` in this directory.",
    ])
    (RESULTS_DIR / "MODEL_CARD.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    if not CACHE_PATH.exists():
        raise FileNotFoundError(f"Missing price cache: {CACHE_PATH}")
    history = pd.read_pickle(CACHE_PATH)
    RESULTS_DIR.mkdir(exist_ok=True)
    ARTIFACT_PATH.parent.mkdir(exist_ok=True)
    artifact = {
        "version": "professional-ml-v1",
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "data_through": str(max(frame.index.max() for frame in history.values()).date()),
        "features": FEATURES,
        "training_universe": sorted(TRAINING_UNIVERSE),
        "test_years": list(TEST_YEARS),
        "horizons": {},
    }
    all_folds = []
    all_predictions = []
    for horizon in HORIZONS:
        dataset = prepare_dataset(history, horizon)
        model, folds, predictions = train_horizon(dataset, horizon)
        artifact["horizons"][str(horizon)] = model
        all_folds.extend(folds)
        all_predictions.append(predictions)
        print(
            f"{horizon:>2} sessions: {model['quality']} · "
            f"Brier skill {model['walk_forward']['brier_skill']:.2%} · "
            f"return correlation {model['walk_forward']['return_correlation']:.3f}"
        )
    with ARTIFACT_PATH.open("w", encoding="utf-8") as handle:
        json.dump(artifact, handle, indent=2, sort_keys=True)
    folds = pd.DataFrame(all_folds)
    predictions = pd.concat(all_predictions, ignore_index=True)
    folds.to_csv(RESULTS_DIR / "walk_forward_folds.csv", index=False)
    predictions.to_csv(RESULTS_DIR / "walk_forward_predictions.csv", index=False)
    write_model_card(artifact, folds)
    print(f"Wrote {ARTIFACT_PATH}")


if __name__ == "__main__":
    main()

