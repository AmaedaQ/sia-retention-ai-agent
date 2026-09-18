# Notebooks

## `01_data_pipeline.py` (Phase 1 — done)

Loads the real [IBM/Kaggle Telco Customer Churn dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
(~7,043 customers), cleans it (drops the 11 rows with a blank
`TotalCharges` -- brand-new customers with tenure 0), runs a short EDA
(churn rate lands at 26.58%, matching the dataset's known public
benchmark), adds four clearly-documented **synthetic bridge** columns for
the fields this dataset doesn't have (`data_usage_gb`,
`signal_strength_score`, `days_since_last_recharge`,
`support_tickets_open` -- see the module docstring and
`data/processed/DATASET_CARD.md` for exactly what's real vs. fabricated),
validates every row against `backend/schemas.py`'s `Subscriber` model,
and writes a stratified 70/15/15 train/val/test split to
`data/processed/`.

Run locally or in Colab:
```
pip install -r requirements.txt
python notebooks/01_data_pipeline.py
```

Tests: `tests/test_data_pipeline.py` (includes a test that the synthetic
columns do NOT correlate with churn -- that's the whole point of keeping
them separate from a model's real training signal).

`scripts/push_to_hf.py` pushes `data/processed/` to a public Hugging
Face Dataset repo. It is **written but not run from here** -- this
account's network policy blocks huggingface.co from both the cloud
sandbox and the linked device, so run it from Colab or your own machine
(see the script's docstring for exact steps).

## `02_train_model.py` (Phase 2 — code written, not yet run)

Trains an XGBoost classifier on `data/processed/`, evaluates it on
train/val/test, and -- the honest part -- scores the OLD hand-written
formula from `backend/data_generator.py` on the exact same test rows
with the same metric (ROC-AUC), so the comparison in `artifacts/metrics.json`
is real, not asserted. Explains the model globally with SHAP
(`explain_global`), ranking features by mean |SHAP| on the test split.

This has NOT been executed yet: installing scikit-learn/xgboost/shap on
this account's linked device timed out repeatedly (dependency resolution
took longer than the shell's time budget), so it needs to run in Colab,
where installs are fast and a free GPU/CPU is available. `tests/test_train_model.py`
has 5 tests on tiny synthetic data (`pytest.importorskip` skips them
gracefully wherever xgboost/shap aren't installed) -- run those first in
Colab to catch any issue before the real training run.

Run in Colab:
```
!git clone https://github.com/AmaedaQ/sia-retention-ai-agent.git
%cd sia-retention-ai-agent
!pip install -q scikit-learn xgboost shap joblib
!python -m pytest tests/test_train_model.py -v
!python notebooks/02_train_model.py
```

`scripts/push_model_to_hf.py` pushes `artifacts/` to a public Hugging
Face Model repo (also not run from here -- same network restriction as
Phase 1's dataset push).

See the execution plan doc for the full phase breakdown.
