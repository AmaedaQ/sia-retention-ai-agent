# Notebooks

`01_data_pipeline.ipynb` (Phase 1, not yet written) will load the
[IBM/Kaggle Telco Customer Churn dataset](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
in Google Colab, clean it, align its columns to `backend/schemas.py`'s
`Subscriber` model, and push the result to a public Hugging Face Dataset
repo.

`02_train_model.ipynb` (Phase 2, not yet written) will train and evaluate
the churn model and push it to Hugging Face Model Hub.

Run notebooks in Colab (Runtime → free GPU/CPU as needed), not locally —
see the execution plan doc for the full phase breakdown.
