"""Tests for notebooks/02_train_model.py -- fast, on tiny synthetic data,
so they run in CI without needing the real dataset or a GPU."""

import importlib.util
import os
import sys

import numpy as np
import pandas as pd
import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(_ROOT)

xgboost = pytest.importorskip("xgboost")
shap = pytest.importorskip("shap")

_spec = importlib.util.spec_from_file_location(
    "sia_train_model", os.path.join(_ROOT, "notebooks", "02_train_model.py")
)
train_model = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(train_model)


def _toy_subscribers(n=300, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "user_id": [f"U{i:04d}" for i in range(n)],
            "avg_monthly_spend": rng.uniform(20, 120, size=n),
            "data_usage_gb": rng.uniform(0, 60, size=n),
            "days_since_last_recharge": rng.integers(0, 45, size=n),
            "signal_strength_score": rng.beta(5, 2, size=n),
            "active_plan": rng.choice(["Flexi", "Standard", "Premium"], size=n),
            "support_tickets_open": rng.poisson(0.6, size=n),
            "churn": rng.choice([0, 1], size=n, p=[0.73, 0.27]),
        }
    )


def test_prepare_features_one_hot_encodes_plan():
    df = _toy_subscribers()
    X, y = train_model.prepare_features(df)
    assert any(c.startswith("plan_") for c in X.columns)
    assert len(y) == len(df)


def test_prepare_features_reindexes_missing_plan_category():
    train_df = _toy_subscribers(n=300, seed=1)
    # a split that only has one plan category, unlike training
    small_df = train_df[train_df["active_plan"] == "Flexi"].head(10).copy()

    X_train, _ = train_model.prepare_features(train_df)
    X_small, _ = train_model.prepare_features(small_df, reference_columns=list(X_train.columns))

    assert list(X_small.columns) == list(X_train.columns)
    # the plan columns the small split doesn't have should be all zero, not missing
    assert (X_small[[c for c in X_train.columns if c.startswith("plan_") and c != "plan_Flexi"]] == 0).all().all()


def test_baseline_formula_score_matches_known_weights():
    df = pd.DataFrame(
        {
            "days_since_last_recharge": [0, 45],
            "signal_strength_score": [1.0, 0.0],
            "support_tickets_open": [0, 5],
        }
    )
    scores = train_model.baseline_formula_score(df)
    # row 0: perfect recency, perfect signal, no tickets -> risk 0
    assert scores[0] == pytest.approx(0.0)
    # row 1: worst recency (0.4) + worst signal (0.4) + 5 tickets*0.2 (1.0) -> 1.8
    assert scores[1] == pytest.approx(1.8)


def test_train_and_evaluate_smoke():
    df = _toy_subscribers(n=400, seed=2)
    X, y = train_model.prepare_features(df)
    model = train_model.train(X, y)
    formula_scores = train_model.baseline_formula_score(df)
    metrics = train_model.evaluate(model, X, y, formula_scores, "toy")
    assert 0.0 <= metrics["model"]["roc_auc"] <= 1.0
    assert 0.0 <= metrics["old_formula_roc_auc"] <= 1.0
    assert metrics["n"] == len(df)


def test_explain_global_returns_ranked_features():
    df = _toy_subscribers(n=200, seed=3)
    X, y = train_model.prepare_features(df)
    model = train_model.train(X, y)
    top = train_model.explain_global(model, X, top_k=3)
    assert len(top) == 3
    values = [row["mean_abs_shap"] for row in top]
    assert values == sorted(values, reverse=True)
