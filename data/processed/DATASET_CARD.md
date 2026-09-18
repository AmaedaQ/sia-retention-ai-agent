---
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
