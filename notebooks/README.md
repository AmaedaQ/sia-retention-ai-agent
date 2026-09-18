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

## `02_train_model.ipynb` (Phase 2, not yet written)

Will train and evaluate the churn model on `data/processed/` and push it
to Hugging Face Model Hub.

See the execution plan doc for the full phase breakdown.
