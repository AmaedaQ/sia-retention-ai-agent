"""Pushes data/processed/ to a public Hugging Face Dataset repo.

This script is written but NOT run by Claude -- huggingface.co is blocked
by this account's network egress policy from both the cloud sandbox and
the linked device, so this step has to run somewhere with real internet:
Google Colab, or your own machine with `pip install huggingface_hub`.

Usage:
    export HF_TOKEN=hf_...                 # from huggingface.co/settings/tokens (write access)
    export HF_DATASET_REPO=<your-username>/sia-churn-dataset
    python scripts/push_to_hf.py

What it does:
    1. Creates the dataset repo (if it doesn't already exist).
    2. Uploads train.csv, val.csv, test.csv from data/processed/.
    3. Uploads DATASET_CARD.md as the repo's README.md (this is what
       renders as the dataset's description page on Hugging Face).
"""

import os
import sys

try:
    from huggingface_hub import HfApi, create_repo
except ImportError:
    sys.exit("huggingface_hub not installed -- run: pip install huggingface_hub")

TOKEN = os.environ.get("HF_TOKEN")
REPO_ID = os.environ.get("HF_DATASET_REPO")
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "processed")

if not TOKEN:
    sys.exit("Set HF_TOKEN (a Hugging Face access token with write scope) before running this.")
if not REPO_ID:
    sys.exit("Set HF_DATASET_REPO (e.g. yourname/sia-churn-dataset) before running this.")

required = ["train.csv", "val.csv", "test.csv", "DATASET_CARD.md"]
missing = [f for f in required if not os.path.exists(os.path.join(DATA_DIR, f))]
if missing:
    sys.exit(f"Missing {missing} in {DATA_DIR} -- run notebooks/01_data_pipeline.py first.")

api = HfApi(token=TOKEN)

print(f"Creating (or reusing) dataset repo {REPO_ID} ...")
create_repo(REPO_ID, token=TOKEN, repo_type="dataset", exist_ok=True)

for fname, dest in [
    ("train.csv", "train.csv"),
    ("val.csv", "val.csv"),
    ("test.csv", "test.csv"),
    ("DATASET_CARD.md", "README.md"),
]:
    print(f"Uploading {fname} -> {dest} ...")
    api.upload_file(
        path_or_fileobj=os.path.join(DATA_DIR, fname),
        path_in_repo=dest,
        repo_id=REPO_ID,
        repo_type="dataset",
    )

print(f"Done: https://huggingface.co/datasets/{REPO_ID}")
