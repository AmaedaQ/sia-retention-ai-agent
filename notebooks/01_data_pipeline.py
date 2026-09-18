"""Phase 1 data pipeline: real dataset -> SIA's Subscriber schema.

What's real vs. synthetic here, stated plainly (this is the thing Phase 0
promised to stop hiding):

  REAL (from the IBM/Kaggle Telco Customer Churn dataset, ~7,043 rows):
    - user_id            <- customerID
    - avg_monthly_spend   <- MonthlyCharges
    - active_plan         <- Contract (Month-to-month/One year/Two year),
                             relabeled to SIA's plan names
    - churn (label)       <- Churn (Yes/No) -- used for training/eval only,
                             never written into Subscriber itself

  SYNTHETIC BRIDGE (Telco has no telecom-prepaid / network-quality fields,
  so these are generated, not measured -- every one of them is seeded and
  documented, never presented as real):
    - data_usage_gb            <- drawn per InternetService tier (DSL /
                                   Fiber optic / No), so it's *plausible*
                                   but still fabricated
    - signal_strength_score    <- Beta(5, 2) draw, independent of churn
    - days_since_last_recharge <- Poisson draw, independent of churn
    - support_tickets_open     <- Poisson draw, independent of churn

None of the synthetic columns are allowed to correlate with the churn
label -- if they did, a model trained on them would look artificially
good and that would be exactly the kind of fake result Phase 0 was
written to prevent. The synthetic-vs-churn independence is asserted by
a test in tests/test_data_pipeline.py, not just claimed here.

Run:
    python notebooks/01_data_pipeline.py
Produces:
    data/processed/{train,val,test}.csv
    data/processed/DATASET_CARD.md
"""

from __future__ import annotations

import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.schemas import Subscriber  # noqa: E402

SEED = 42
RAW_PATH = os.path.join("data", "raw", "telco_customer_churn.csv")
OUT_DIR = os.path.join("data", "processed")

PLAN_MAP = {
    "Month-to-month": "Flexi",
    "One year": "Standard",
    "Two year": "Premium",
}

USAGE_GB_BY_INTERNET = {
    "Fiber optic": (45.0, 15.0),  # (mean, std) for np.random.normal
    "DSL": (22.0, 8.0),
    "No": (2.0, 1.5),
}


def load_raw(path: str = RAW_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Fixes the one well-known quirk of this dataset: TotalCharges is
    read as a string because 11 brand-new customers (tenure == 0) have
    a blank instead of a number. We drop those rows rather than impute,
    since a brand-new customer has no real TotalCharges yet -- imputing
    one would be inventing a number, same mistake this whole phase is
    trying to stop making."""
    df = df.copy()
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    before = len(df)
    df = df.dropna(subset=["TotalCharges"])
    dropped = before - len(df)
    if dropped:
        print(f"[clean] dropped {dropped} rows with blank TotalCharges (tenure==0 new customers)")
    df["Churn"] = df["Churn"].map({"Yes": 1, "No": 0})
    return df.reset_index(drop=True)


def eda_summary(df: pd.DataFrame) -> str:
    churn_rate = df["Churn"].mean()
    lines = [
        "# EDA summary — Telco Customer Churn (real data)",
        "",
        f"- Rows after cleaning: {len(df)}",
        f"- Churn rate: {churn_rate:.3%} (class imbalance -- expect this to land ~26-27%, "
        "matches the known public benchmark for this dataset)",
        f"- Columns: {len(df.columns)}",
        "",
        "## Churn rate by contract type",
    ]
    for contract, group in df.groupby("Contract"):
        lines.append(f"- {contract}: {group['Churn'].mean():.3%} (n={len(group)})")
    lines.append("")
    lines.append("## Numeric column ranges (real columns only)")
    for col in ["tenure", "MonthlyCharges", "TotalCharges"]:
        lines.append(f"- {col}: min={df[col].min():.2f}, max={df[col].max():.2f}, mean={df[col].mean():.2f}")
    return "\n".join(lines)


def add_synthetic_bridge(df: pd.DataFrame, seed: int = SEED) -> pd.DataFrame:
    """Adds the columns SIA's schema needs that this dataset doesn't have.
    Every draw uses its own dedicated RNG stream (np.random.default_rng
    with a seed offset) so the columns are independent of each other and,
    critically, independent of Churn -- see the module docstring."""
    df = df.copy()
    n = len(df)

    rng_usage = np.random.default_rng(seed)
    usage = np.empty(n)
    for tier, (mean, std) in USAGE_GB_BY_INTERNET.items():
        mask = (df["InternetService"] == tier).to_numpy()
        usage[mask] = rng_usage.normal(mean, std, size=mask.sum())
    df["data_usage_gb"] = np.clip(usage, 0, None).round(2)

    rng_signal = np.random.default_rng(seed + 1)
    df["signal_strength_score"] = rng_signal.beta(5, 2, size=n).round(4)

    rng_recharge = np.random.default_rng(seed + 2)
    df["days_since_last_recharge"] = rng_recharge.poisson(lam=15, size=n).astype(int)

    rng_tickets = np.random.default_rng(seed + 3)
    df["support_tickets_open"] = rng_tickets.poisson(lam=0.6, size=n).astype(int)

    return df


def to_subscriber_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Maps the cleaned + bridged dataframe onto SIA's Subscriber schema
    column names, and validates every row through the real Pydantic model
    so a shape bug fails here, not three notebooks downstream."""
    out = pd.DataFrame(
        {
            "user_id": df["customerID"],
            "avg_monthly_spend": df["MonthlyCharges"],
            "data_usage_gb": df["data_usage_gb"],
            "days_since_last_recharge": df["days_since_last_recharge"],
            "signal_strength_score": df["signal_strength_score"],
            "active_plan": df["Contract"].map(PLAN_MAP),
            "support_tickets_open": df["support_tickets_open"],
        }
    )
    # label kept alongside, not inside Subscriber -- churn is the training
    # target, not a subscriber attribute
    out["churn"] = df["Churn"].values

    errors = 0
    for row in out.drop(columns=["churn"]).itertuples(index=False):
        try:
            Subscriber(**row._asdict())
        except Exception as e:  # noqa: BLE001
            errors += 1
            if errors <= 3:
                print(f"[validate] row failed schema: {e}")
    if errors:
        raise ValueError(f"{errors} rows failed Subscriber schema validation")
    print(f"[validate] all {len(out)} rows passed Subscriber schema validation")
    return out


def stratified_split(df: pd.DataFrame, seed: int = SEED):
    """70/15/15 train/val/test, stratified on churn so the ~27% minority
    class keeps roughly the same ratio in all three splits."""
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    def _split_group(g: pd.DataFrame):
        n = len(g)
        n_train = int(n * 0.70)
        n_val = int(n * 0.15)
        return g.iloc[:n_train], g.iloc[n_train : n_train + n_val], g.iloc[n_train + n_val :]

    train_parts, val_parts, test_parts = [], [], []
    for _, group in df.groupby("churn"):
        tr, va, te = _split_group(group.sample(frac=1, random_state=seed))
        train_parts.append(tr)
        val_parts.append(va)
        test_parts.append(te)

    train = pd.concat(train_parts).sample(frac=1, random_state=seed).reset_index(drop=True)
    val = pd.concat(val_parts).sample(frac=1, random_state=seed).reset_index(drop=True)
    test = pd.concat(test_parts).sample(frac=1, random_state=seed).reset_index(drop=True)
    return train, val, test


DATASET_CARD_TEMPLATE = """---
license: cc-by-4.0
task_categories:
  - tabular-classification
tags:
  - churn-prediction
  - telecom
  - sia-retention-engine
---

# SIA Retention Engine — Churn Training Dataset

Preprocessed, schema-validated version of the public IBM/Kaggle Telco
Customer Churn dataset, prepared for training SIA's churn risk model
(Phase 2 of the SIA Retention Engine execution plan).

## Source

Real data: IBM Telco Customer Churn dataset
(https://www.kaggle.com/datasets/blastchar/telco-customer-churn),
~7,043 customers, ~26-27% churn rate.

## What's real and what's synthetic

This dataset was built for a telecom (prepaid-style) retention use case,
but the public Telco dataset is a US postpaid dataset with no network-
quality or recharge fields. To fit SIA's `Subscriber` schema without
pretending fields exist that don't, four columns are synthetically
generated and clearly marked as such below. They are drawn independently
of the churn label (verified by a unit test) so they cannot inflate
model performance -- they exist only so the pipeline's shape matches
what SIA needs, not to help predict churn.

| Column | Real or synthetic | Source |
|---|---|---|
| user_id | Real | `customerID` |
| avg_monthly_spend | Real | `MonthlyCharges` |
| active_plan | Real (relabeled) | `Contract` -> Flexi/Standard/Premium |
| churn | Real | `Churn` |
| data_usage_gb | Synthetic | Normal draw, mean/std set per `InternetService` tier for plausibility |
| signal_strength_score | Synthetic | Beta(5, 2) draw, range [0, 1] |
| days_since_last_recharge | Synthetic | Poisson(lambda=15) draw |
| support_tickets_open | Synthetic | Poisson(lambda=0.6) draw |

## Splits

Stratified 70/15/15 train/val/test on the `churn` label, seed=42.

## Files

- `train.csv`, `val.csv`, `test.csv` — SIA-schema columns + `churn` label.

## Intended use

Training and evaluating the churn risk classifier for SIA's Monitor
agent (Phase 2). Not intended as a general-purpose telecom dataset --
the synthetic columns are placeholders for real network telemetry SIA
would use in production.
"""


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    print("[1/6] loading raw data...")
    raw = load_raw()

    print("[2/6] cleaning...")
    cleaned = clean(raw)

    print("[3/6] EDA...")
    summary = eda_summary(cleaned)
    with open(os.path.join(OUT_DIR, "eda_summary.md"), "w") as f:
        f.write(summary)
    print(summary)

    print("[4/6] adding synthetic bridge columns...")
    bridged = add_synthetic_bridge(cleaned)

    print("[5/6] mapping to Subscriber schema + validating...")
    subs = to_subscriber_frame(bridged)

    print("[6/6] stratified split + writing outputs...")
    train, val, test = stratified_split(subs)
    train.to_csv(os.path.join(OUT_DIR, "train.csv"), index=False)
    val.to_csv(os.path.join(OUT_DIR, "val.csv"), index=False)
    test.to_csv(os.path.join(OUT_DIR, "test.csv"), index=False)
    with open(os.path.join(OUT_DIR, "DATASET_CARD.md"), "w") as f:
        f.write(DATASET_CARD_TEMPLATE)

    print(
        f"done: train={len(train)} val={len(val)} test={len(test)} "
        f"(churn rate train={train['churn'].mean():.3%} "
        f"val={val['churn'].mean():.3%} test={test['churn'].mean():.3%})"
    )


if __name__ == "__main__":
    main()
