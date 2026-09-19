import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from backend.models.loader import ModelUnavailable
from backend.models.predict import score_subscribers
from config.settings import settings

_warned_plan_mismatch = False


def _score_with_model(df: pd.DataFrame) -> pd.DataFrame:
    """Scores every row with the trained model, replacing the static
    churn_risk_score column that jazz_users.csv was generated with.

    Fixed bug, documented so it isn't reintroduced: jazz_users.csv's
    active_plan values used to be placeholder names ("Weekly Mega",
    "Monthly Super", "Daily Social") that didn't match the plan
    categories the model was actually trained on (Flexi / Standard /
    Premium, from the real Telco dataset's Contract field), and
    avg_monthly_spend was drawn from a ~200-5000 range vs. the model's
    real training range of ~18-119. Combined, every demo row landed far
    outside the model's training distribution on its single strongest
    predictor (plan type, per Phase 2's SHAP analysis) and its spend
    feature -- which silently collapsed every prediction toward one
    extreme and made every scan return 0 flagged customers with no
    visible error. data_generator.py now draws both fields on the same
    scale/vocabulary the model was trained on (see its own comment and
    data/processed/DATASET_CARD.md). This function keeps the
    all-zero-plan check below as a guard in case that ever regresses.
    """
    global _warned_plan_mismatch
    records = df.to_dict(orient="records")
    predictions = score_subscribers(records)

    if not _warned_plan_mismatch:
        plan_cols_all_zero = sum(
            1 for p in predictions if not any(f.feature.startswith("plan_") for f in p.top_factors)
        )
        if plan_cols_all_zero:
            print(
                f"[MONITOR] note: {plan_cols_all_zero}/{len(predictions)} rows have an active_plan "
                "value the model wasn't trained on (see _score_with_model's docstring) -- "
                "scores still computed, just without plan-type signal for those rows."
            )
        _warned_plan_mismatch = True

    by_id = {p.user_id: p for p in predictions}
    df = df.copy()
    df["churn_risk_score"] = df["user_id"].map(lambda uid: by_id[str(uid)].churn_risk_score)
    df["risk_source"] = "model"
    return df


def monitor_churn_risks(threshold=0.7):
    """Scan users and filter those above the churn risk threshold.

    When USE_ML_MODEL is on and the trained model loads successfully,
    every user is re-scored with the real model (see _score_with_model)
    instead of trusting the static churn_risk_score column baked into
    jazz_users.csv at generation time. On any failure to load or run the
    model, falls straight back to the original CSV-column behavior --
    the caller never sees the difference except in the risk_source field.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'jazz_users.csv')
    log_path = os.path.join(base_dir, 'data', 'action_logs.csv')

    try:
        if not os.path.exists(data_path):
            print(f"File not found: {data_path}")
            return []

        df = pd.read_csv(data_path)

        if settings.use_ml_model:
            try:
                df = _score_with_model(df)
            except ModelUnavailable as e:
                print(f"[MONITOR] ML model unavailable ({e}) -- falling back to the formula's stored scores.")
                df["risk_source"] = "formula"
            except Exception as e:  # noqa: BLE001 -- a scoring bug must degrade to the
                # formula, never silently zero out every user. This is deliberately
                # broader than ModelUnavailable: loader.py already wraps every load
                # failure as ModelUnavailable, so anything landing here is a bug in
                # the scoring path itself (predict.py) -- still not something that
                # should turn a scan into "0 customers flagged" with no visible error.
                print(f"[MONITOR] ML scoring failed unexpectedly ({e!r}) -- falling back to the formula's stored scores.")
                df["risk_source"] = "formula"
        else:
            df["risk_source"] = "formula"

        # Filter users above threshold
        risky_users = df[df['churn_risk_score'] >= threshold].copy()

        # SMART MEMORY: Exclude users who already received an offer
        if os.path.exists(log_path):
            logs = pd.read_csv(log_path)
            processed_ids = logs['user_id'].unique()
            risky_users = risky_users[~risky_users['user_id'].isin(processed_ids)]

        return risky_users.sort_values(by='churn_risk_score', ascending=False).to_dict(orient='records')
    except Exception as e:
        print(f"Monitor Agent Error: {e}")
        return []
