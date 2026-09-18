"""Phase 2: train, evaluate and explain the churn risk model.

Meant to run in Google Colab (free GPU/CPU is plenty for a dataset this
size -- training takes seconds, not minutes). Can also run locally:

    pip install -r requirements.txt
    python notebooks/02_train_model.py

Produces:
    artifacts/model.joblib          -- the trained XGBoost classifier
    artifacts/feature_columns.json  -- exact column order the model expects
    artifacts/metrics.json          -- train/val/test metrics + the honest
                                        comparison against the old formula
    artifacts/MODEL_CARD.md         -- for the Hugging Face Model Hub push

What makes this an honest comparison, not just a new number: the old
hand-written formula from backend/data_generator.py --
    risk = (days_since_last_recharge / 45) * 0.4
         + (1 - signal_strength_score) * 0.4
         + support_tickets_open * 0.2
-- is evaluated on the SAME real test split as the trained model, using
the SAME metric (ROC-AUC). If the model doesn't beat the formula here,
that's reported too, not hidden.
"""

from __future__ import annotations

import json
import os
import sys

import joblib
import numpy as np
import pandas as pd
import shap
import xgboost as xgb
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_DIR = os.path.join("data", "processed")
ARTIFACT_DIR = "artifacts"
MODEL_VERSION = "v1.0.0"

NUMERIC_FEATURES = [
    "avg_monthly_spend",
    "data_usage_gb",
    "days_since_last_recharge",
    "signal_strength_score",
    "support_tickets_open",
]
CATEGORICAL_FEATURE = "active_plan"


def load_split(name: str) -> pd.DataFrame:
    return pd.read_csv(os.path.join(DATA_DIR, f"{name}.csv"))


def prepare_features(df: pd.DataFrame, reference_columns: list[str] | None = None):
    """One-hot encodes active_plan and returns (X, y). When
    reference_columns is given (val/test), the result is reindexed to
    exactly match the training columns -- a plan category missing from a
    split becomes an all-zero column instead of silently shifting the
    feature order."""
    X = df[NUMERIC_FEATURES].copy()
    plan_dummies = pd.get_dummies(df[CATEGORICAL_FEATURE], prefix="plan")
    X = pd.concat([X, plan_dummies], axis=1)
    if reference_columns is not None:
        X = X.reindex(columns=reference_columns, fill_value=0)
    y = df["churn"].astype(int)
    return X, y


def baseline_formula_score(df: pd.DataFrame) -> np.ndarray:
    """The original hand-written heuristic from data_generator.py, applied
    to the same rows the model is scored on -- this is what SIA is
    replacing, so it has to be measured on the same footing, not quoted
    from memory."""
    return (
        (df["days_since_last_recharge"] / 45) * 0.4
        + (1 - df["signal_strength_score"]) * 0.4
        + df["support_tickets_open"] * 0.2
    ).to_numpy()


def train(X_train: pd.DataFrame, y_train: pd.Series) -> xgb.XGBClassifier:
    n_pos = max((y_train == 1).sum(), 1)
    n_neg = (y_train == 0).sum()
    scale_pos_weight = n_neg / n_pos  # counters the ~27% churn class imbalance
    model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        scale_pos_weight=scale_pos_weight,
        eval_metric="logloss",
        random_state=42,
    )
    model.fit(X_train, y_train)
    return model


def evaluate(model: xgb.XGBClassifier, X: pd.DataFrame, y: pd.Series, formula_scores: np.ndarray, split_name: str) -> dict:
    proba = model.predict_proba(X)[:, 1]
    preds = (proba >= 0.5).astype(int)
    return {
        "split": split_name,
        "n": int(len(y)),
        "model": {
            "accuracy": round(float(accuracy_score(y, preds)), 4),
            "precision": round(float(precision_score(y, preds, zero_division=0)), 4),
            "recall": round(float(recall_score(y, preds, zero_division=0)), 4),
            "f1": round(float(f1_score(y, preds, zero_division=0)), 4),
            "roc_auc": round(float(roc_auc_score(y, proba)), 4),
        },
        "old_formula_roc_auc": round(float(roc_auc_score(y, formula_scores)), 4),
    }


def explain_global(model: xgb.XGBClassifier, X: pd.DataFrame, top_k: int = 5) -> list[dict]:
    """Mean absolute SHAP value per feature across the given set --
    what the Monitor agent's decider prompt will eventually quote."""
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X)
    mean_abs = np.abs(shap_values).mean(axis=0)
    ranked = sorted(zip(X.columns, mean_abs), key=lambda t: -t[1])[:top_k]
    return [{"feature": f, "mean_abs_shap": round(float(v), 4)} for f, v in ranked]


MODEL_CARD_TEMPLATE = """---
license: cc-by-4.0
tags:
  - tabular-classification
  - churn-prediction
  - xgboost
  - sia-retention-engine
---

# SIA Retention Engine — Churn Risk Model ({version})

XGBoost classifier trained on the SIA Retention Engine's Phase 1 dataset
(real IBM/Kaggle Telco Customer Churn data, mapped to SIA's `Subscriber`
schema — see the dataset repo for exactly what's real vs. synthetic).

## Metrics

See `metrics.json` in this repo for the full train/val/test breakdown,
including a direct ROC-AUC comparison against the original hand-written
heuristic formula it replaces (`backend/data_generator.py`), measured on
the same test split.

## Top features (mean |SHAP|, test split)

{top_features}

## Intended use

Churn risk scoring for SIA's Monitor agent, behind the `USE_ML_MODEL`
feature flag (`config/settings.py`). Falls back to the original formula
when this model isn't loaded — see `backend/models/loader.py`.

## Files

- `model.joblib` — the trained XGBoost classifier (load with `joblib.load`)
- `feature_columns.json` — exact column order/names the model expects
"""


def main():
    os.makedirs(ARTIFACT_DIR, exist_ok=True)

    print("[1/5] loading splits...")
    train_df, val_df, test_df = load_split("train"), load_split("val"), load_split("test")

    print("[2/5] preparing features...")
    X_train, y_train = prepare_features(train_df)
    feature_columns = list(X_train.columns)
    X_val, y_val = prepare_features(val_df, reference_columns=feature_columns)
    X_test, y_test = prepare_features(test_df, reference_columns=feature_columns)

    print("[3/5] training XGBoost...")
    model = train(X_train, y_train)

    print("[4/5] evaluating (model vs. the old formula, same test rows)...")
    results = {
        "model_version": MODEL_VERSION,
        "feature_columns": feature_columns,
        "splits": [
            evaluate(model, X_train, y_train, baseline_formula_score(train_df), "train"),
            evaluate(model, X_val, y_val, baseline_formula_score(val_df), "val"),
            evaluate(model, X_test, y_test, baseline_formula_score(test_df), "test"),
        ],
    }
    top_features = explain_global(model, X_test)
    results["top_features_test"] = top_features
    for row in results["splits"]:
        print(row)
    print("top features:", top_features)

    print("[5/5] saving artifacts...")
    joblib.dump(model, os.path.join(ARTIFACT_DIR, "model.joblib"))
    with open(os.path.join(ARTIFACT_DIR, "feature_columns.json"), "w") as f:
        json.dump(feature_columns, f, indent=2)
    with open(os.path.join(ARTIFACT_DIR, "metrics.json"), "w") as f:
        json.dump(results, f, indent=2)

    top_lines = "\n".join(f"- `{r['feature']}`: {r['mean_abs_shap']}" for r in top_features)
    with open(os.path.join(ARTIFACT_DIR, "MODEL_CARD.md"), "w") as f:
        f.write(MODEL_CARD_TEMPLATE.format(version=MODEL_VERSION, top_features=top_lines))

    test_row = results["splits"][-1]
    print(
        f"\ndone: test ROC-AUC model={test_row['model']['roc_auc']} "
        f"vs. old formula={test_row['old_formula_roc_auc']}"
    )


if __name__ == "__main__":
    main()
