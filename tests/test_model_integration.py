"""Tests for Phase 3: backend/models/loader.py, backend/models/predict.py,
and monitor.py's fallback behavior. All fast, no network and no real
trained model needed -- a fake classifier stands in for the real one, so
these run in CI the same as everything else."""

import os
import sys

import numpy as np
import pandas as pd
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import dataclasses

from backend.models import loader as loader_module
from backend.models import predict as predict_module
from backend.models.loader import LoadedModel, ModelUnavailable
from config.settings import settings


def _patch_settings(monkeypatch, module, **overrides):
    """Settings is a frozen dataclass, so tests replace the module-level
    `settings` name each module bound at import time, rather than
    mutating fields on the shared instance."""
    monkeypatch.setattr(module, "settings", dataclasses.replace(settings, **overrides))


@pytest.fixture(autouse=True)
def _reset_caches():
    """Every test starts from a clean model cache and default settings,
    so one test's monkeypatching can't leak into the next."""
    loader_module.reset_model_cache()
    predict_module._cached_explainer = None
    predict_module._explainer_for_revision = None
    yield
    loader_module.reset_model_cache()
    predict_module._cached_explainer = None
    predict_module._explainer_for_revision = None


def test_load_churn_model_raises_when_flag_off(monkeypatch):
    _patch_settings(monkeypatch, loader_module, use_ml_model=False)
    with pytest.raises(ModelUnavailable, match="USE_ML_MODEL"):
        loader_module.load_churn_model()


def test_load_churn_model_raises_when_repo_not_set(monkeypatch):
    _patch_settings(monkeypatch, loader_module, use_ml_model=True, hf_model_repo="")
    with pytest.raises(ModelUnavailable, match="HF_MODEL_REPO"):
        loader_module.load_churn_model()


def test_get_churn_model_caches_a_failed_load(monkeypatch):
    """A misconfigured repo shouldn't retry a slow network call on every
    single prediction request -- the failure itself is cached."""
    _patch_settings(monkeypatch, loader_module, use_ml_model=False)
    with pytest.raises(ModelUnavailable):
        loader_module.get_churn_model()
    # second call hits the "already failed" branch, not load_churn_model again
    with pytest.raises(ModelUnavailable, match="already failed"):
        loader_module.get_churn_model()


class _FakeModel:
    """Stands in for the real XGBClassifier: deterministic proba based on
    whether any plan_* column is set, so tests can check the feature
    frame was actually built and reindexed correctly."""

    def predict_proba(self, X: pd.DataFrame):
        has_known_plan = X.filter(like="plan_").sum(axis=1) > 0
        p1 = np.where(has_known_plan, 0.8, 0.3)
        return np.column_stack([1 - p1, p1])


def _toy_users(n=5, plan="Flexi"):
    return [
        {
            "user_id": f"U{i:03d}",
            "avg_monthly_spend": 50.0 + i,
            "data_usage_gb": 10.0 + i,
            "days_since_last_recharge": i,
            "signal_strength_score": 0.5,
            "active_plan": plan,
            "support_tickets_open": 0,
        }
        for i in range(n)
    ]


def test_build_feature_frame_reindexes_to_model_columns():
    users_df = pd.DataFrame(_toy_users(n=3, plan="Flexi"))
    feature_columns = [
        "avg_monthly_spend",
        "data_usage_gb",
        "days_since_last_recharge",
        "signal_strength_score",
        "support_tickets_open",
        "plan_Flexi",
        "plan_Premium",
        "plan_Standard",
    ]
    X = predict_module._build_feature_frame(users_df, feature_columns)
    assert list(X.columns) == feature_columns
    assert (X["plan_Flexi"] == 1).all()
    assert (X["plan_Premium"] == 0).all()


def test_build_feature_frame_zeroes_unseen_plan_category():
    """The known jazz_users.csv mismatch: a plan value the model never
    saw during training must become all-zero columns, not a crash."""
    users_df = pd.DataFrame(_toy_users(n=3, plan="Weekly Mega"))
    feature_columns = ["avg_monthly_spend", "data_usage_gb", "days_since_last_recharge",
                        "signal_strength_score", "support_tickets_open",
                        "plan_Flexi", "plan_Premium", "plan_Standard"]
    X = predict_module._build_feature_frame(users_df, feature_columns)
    assert (X[["plan_Flexi", "plan_Premium", "plan_Standard"]] == 0).all().all()


def test_score_subscribers_returns_risk_predictions(monkeypatch):
    fake = LoadedModel(model=_FakeModel(), feature_columns=[
        "avg_monthly_spend", "data_usage_gb", "days_since_last_recharge",
        "signal_strength_score", "support_tickets_open",
        "plan_Flexi", "plan_Premium", "plan_Standard",
    ], revision="test-rev")
    monkeypatch.setattr(predict_module, "get_churn_model", lambda: fake)
    # force the SHAP path to fail gracefully (no real model to explain)
    monkeypatch.setattr(predict_module, "_get_explainer", lambda loaded: (_ for _ in ()).throw(RuntimeError("no shap in test")))

    users = _toy_users(n=2, plan="Flexi")
    predictions = predict_module.score_subscribers(users)

    assert len(predictions) == 2
    assert all(p.source == "model" for p in predictions)
    assert all(p.model_revision == "test-rev" for p in predictions)
    assert all(0.0 <= p.churn_risk_score <= 1.0 for p in predictions)
    assert all(p.top_factors == [] for p in predictions)  # SHAP failed -> empty, not a crash


def test_score_subscribers_empty_list_returns_empty():
    assert predict_module.score_subscribers([]) == []
