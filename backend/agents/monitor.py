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

    Known limitation, surfaced rather than hidden: jazz_users.csv's
    active_plan values ("Weekly Mega", "Monthly Super", "Daily Social")
    are this demo dataset's original placeholder names -- they don't
    match the plan categories the model was actually trained on (Flexi /
    Standard / Premium, derived from the real Telco dataset's Contract
    field in Phase 1). The model still scores these rows fine on the
    other four real-shaped features, but treats every row's plan as
    "unknown" (all plan_* columns zero) rather than using plan type,
    which Phase 2's SHAP analysis found to be the single strongest
    predictor. Scores on this specific demo file are usable but weaker
    than they'd be on data whose plan names actually match training --
    worth aligning data_generator.py's plan names to Flexi/Standard/
    Premium if this demo data is going to be used for more than a UI demo.
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
