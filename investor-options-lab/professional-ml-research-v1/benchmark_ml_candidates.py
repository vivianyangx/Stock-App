"""Benchmark compact tabular classifiers without promoting a winner automatically."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from train_professional_model import CACHE_PATH, FEATURES, HORIZONS, prepare_dataset


def candidates() -> dict:
    return {
        "Logistic": make_pipeline(
            SimpleImputer(strategy="median"), StandardScaler(),
            LogisticRegression(C=.10, max_iter=1500),
        ),
        "HistogramGB": make_pipeline(
            SimpleImputer(strategy="median"),
            HistGradientBoostingClassifier(
                learning_rate=.035, max_iter=160, max_leaf_nodes=15,
                min_samples_leaf=120, l2_regularization=8.0,
                random_state=20261118,
            ),
        ),
        "ExtraTrees": make_pipeline(
            SimpleImputer(strategy="median"),
            ExtraTreesClassifier(
                n_estimators=240, max_depth=7, min_samples_leaf=80,
                max_features=.65, n_jobs=-1, random_state=20261118,
            ),
        ),
    }


def main() -> None:
    history = pd.read_pickle(CACHE_PATH)
    rows = []
    for horizon in HORIZONS:
        data = prepare_dataset(history, horizon)
        for year in range(2021, 2026):
            start, end = pd.Timestamp(f"{year}-01-01"), pd.Timestamp(f"{year}-12-31")
            train = data.loc[(data.date < start) & (data.label_date < start)]
            test = data.loc[data.date.between(start, end)]
            x_train, y_train = train[FEATURES], train.target_up
            x_test, y_test = test[FEATURES], test.target_up
            baseline = np.repeat(float(y_train.mean()), len(test))
            baseline_brier = brier_score_loss(y_test, baseline)
            for name, model in candidates().items():
                model.fit(x_train, y_train)
                probability = model.predict_proba(x_test)[:, 1]
                brier = brier_score_loss(y_test, probability)
                rows.append({
                    "horizon": horizon, "year": year, "model": name,
                    "brier_skill": 1 - brier / baseline_brier,
                    "auc": roc_auc_score(y_test, probability),
                    "balanced_accuracy": balanced_accuracy_score(y_test, probability >= .5),
                })
                print(horizon, year, name, f"skill={1-brier/baseline_brier:+.2%}",
                      f"auc={roc_auc_score(y_test, probability):.3f}")
    result = pd.DataFrame(rows)
    print("\nAVERAGE BY MODEL")
    print(result.groupby(["horizon", "model"])[["brier_skill", "auc", "balanced_accuracy"]]
          .agg(["mean", "std"]).round(4).to_string())
    print("\n2025 UNTOUCHED COMPARISON")
    print(result.loc[result.year.eq(2025)].round(4).to_string(index=False))


if __name__ == "__main__":
    main()

