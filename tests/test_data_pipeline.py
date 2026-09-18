"""Tests for the Phase 1 data pipeline (notebooks/01_data_pipeline.py).

The one thing these tests exist to catch: a synthetic bridge column that
accidentally correlates with the churn label, which would make Phase 2's
model look better than it actually is on real signal.
"""

import importlib.util
import os
import sys

import numpy as np
import pandas as pd

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(_ROOT)

# notebooks/01_data_pipeline.py starts with a digit, so it can't be
# imported as a normal module path -- load it directly by file path.
_spec = importlib.util.spec_from_file_location(
    "sia_data_pipeline", os.path.join(_ROOT, "notebooks", "01_data_pipeline.py")
)
pipeline = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pipeline)


def _toy_frame(n=200, seed=0):
    rng = np.random.default_rng(seed)
    return pd.DataFrame(
        {
            "customerID": [f"C{i:04d}" for i in range(n)],
            "MonthlyCharges": rng.uniform(20, 120, size=n).round(2),
            "TotalCharges": rng.uniform(20, 5000, size=n).astype(str),
            "Contract": rng.choice(["Month-to-month", "One year", "Two year"], size=n),
            "InternetService": rng.choice(["DSL", "Fiber optic", "No"], size=n),
            "Churn": rng.choice(["Yes", "No"], size=n, p=[0.27, 0.73]),
        }
    )


def test_clean_drops_blank_total_charges():
    df = _toy_frame(n=20)
    df.loc[0, "TotalCharges"] = ""  # simulate the real dataset's known quirk
    cleaned = pipeline.clean(df)
    assert len(cleaned) == 19
    assert set(cleaned["Churn"].unique()) <= {0, 1}


def test_synthetic_bridge_is_deterministic():
    df = pipeline.clean(_toy_frame(n=50))
    a = pipeline.add_synthetic_bridge(df, seed=42)
    b = pipeline.add_synthetic_bridge(df, seed=42)
    pd.testing.assert_series_equal(a["signal_strength_score"], b["signal_strength_score"])
    pd.testing.assert_series_equal(a["data_usage_gb"], b["data_usage_gb"])


def test_synthetic_columns_are_independent_of_churn():
    """The load-bearing test: none of the fabricated columns may leak
    predictive signal about churn, or Phase 2's model evaluation would be
    measuring noise dressed up as accuracy."""
    df = pipeline.clean(_toy_frame(n=2000, seed=1))
    bridged = pipeline.add_synthetic_bridge(df, seed=42)

    for col in ["signal_strength_score", "days_since_last_recharge", "support_tickets_open"]:
        corr = np.corrcoef(bridged[col], bridged["Churn"])[0, 1]
        assert abs(corr) < 0.08, f"{col} correlates with churn (r={corr:.3f}) -- bridge column must stay independent"


def test_to_subscriber_frame_validates_against_schema():
    df = pipeline.clean(_toy_frame(n=30))
    bridged = pipeline.add_synthetic_bridge(df)
    subs = pipeline.to_subscriber_frame(bridged)
    assert len(subs) == 30
    assert set(subs["active_plan"].unique()) <= {"Flexi", "Standard", "Premium"}
    assert subs["signal_strength_score"].between(0, 1).all()


def test_stratified_split_preserves_churn_ratio():
    df = pipeline.clean(_toy_frame(n=2000, seed=2))
    bridged = pipeline.add_synthetic_bridge(df)
    subs = pipeline.to_subscriber_frame(bridged)
    train, val, test = pipeline.stratified_split(subs)

    overall = subs["churn"].mean()
    for split in (train, val, test):
        assert abs(split["churn"].mean() - overall) < 0.03
    # no leakage between splits
    assert set(train["user_id"]) & set(val["user_id"]) == set()
    assert set(train["user_id"]) & set(test["user_id"]) == set()
    assert set(val["user_id"]) & set(test["user_id"]) == set()
