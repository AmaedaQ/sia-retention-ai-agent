"""Scores subscribers with the trained model (Phase 3) -- the piece that
turns Phase 2's offline notebook metrics into a live prediction the
Monitor agent can actually call.

Feature engineering here MUST match notebooks/02_train_model.py's
prepare_features exactly (same numeric columns, same one-hot scheme on
active_plan), or the model silently sees a different feature space than
the one it was trained on. Rather than duplicate that logic and let the
two drift apart, both re-derive their column list the same way: numeric
features in a fixed order, then pd.get_dummies(active_plan), then
reindexed to the model's own feature_columns.json -- so a plan category
the model never saw during training (see the known active_plan mismatch
noted in backend/agents/monitor.py) becomes an all-zero column instead of
crashing or silently misaligning the feature order.
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.models.loader import LoadedModel, get_churn_model
from backend.schemas import RiskPrediction, SHAPFactor
from config.settings import settings

NUMERIC_FEATURES = [
    "avg_monthly_spend",
    "data_usage_gb",
    "days_since_last_recharge",
    "signal_strength_score",
    "support_tickets_open",
]
CATEGORICAL_FEATURE = "active_plan"

_cached_explainer = None
_explainer_for_revision: str | None = None


def _build_feature_frame(users_df: pd.DataFrame, feature_columns: list) -> pd.DataFrame:
    X = users_df[NUMERIC_FEATURES].copy()
    plan_dummies = pd.get_dummies(users_df[CATEGORICAL_FEATURE], prefix="plan")
    X = pd.concat([X, plan_dummies], axis=1)
    return X.reindex(columns=feature_columns, fill_value=0)


def _get_explainer(loaded: LoadedModel):
    """SHAP TreeExplainer construction has real cost -- build it once per
    model revision, not once per prediction batch."""
    global _cached_explainer, _explainer_for_revision
    if _cached_explainer is None or _explainer_for_revision != loaded.revision:
        import shap

        _cached_explainer = shap.TreeExplainer(loaded.model)
        _explainer_for_revision = loaded.revision
    return _cached_explainer


def score_subscribers(users: list[dict]) -> list[RiskPrediction]:
    """Scores a batch of subscriber dicts (the same shape monitor.py reads
    off jazz_users.csv) with the trained model, including per-row SHAP
    top factors. Raises ModelUnavailable if the model can't be loaded --
    callers fall back to the formula on that, same contract as before."""
    if not users:
        return []

    loaded = get_churn_model()  # raises ModelUnavailable if not ready
    users_df = pd.DataFrame(users)
    X = _build_feature_frame(users_df, loaded.feature_columns)

    proba = loaded.model.predict_proba(X)[:, 1]

    try:
        explainer = _get_explainer(loaded)
        shap_values = explainer.shap_values(X)
    except Exception:  # noqa: BLE001 -- explainability is best-effort, never blocks a score
        shap_values = None

    predictions = []
    for i, user in enumerate(users_df.itertuples(index=False)):
        top_factors = []
        if shap_values is not None:
            row_shap = shap_values[i]
            ranked = sorted(
                zip(X.columns, X.iloc[i].to_numpy(), row_shap),
                key=lambda t: -abs(t[2]),
            )[: settings.shap_top_k]
            top_factors = [
                SHAPFactor(feature=f, value=float(v), impact=float(s)) for f, v, s in ranked
            ]
        predictions.append(
            RiskPrediction(
                user_id=str(getattr(user, "user_id")),
                churn_risk_score=float(np.clip(proba[i], 0.0, 1.0)),
                source="model",
                model_revision=loaded.revision,
                top_factors=top_factors,
            )
        )
    return predictions
