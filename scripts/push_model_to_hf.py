"""Pushes the trained model (artifacts/) to a public Hugging Face Model repo.

Same situation as scripts/push_to_hf.py: huggingface.co is blocked by this
account's network policy from both the cloud sandbox and the linked
device, so this has to run somewhere with real internet -- Colab, right
after notebooks/02_train_model.py produces artifacts/.

Usage:
    export HF_TOKEN=hf_...                          # write-scope token
    export HF_MODEL_REPO=<your-username>/sia-churn-model
    python scripts/push_model_to_hf.py

Then set, in .env (or Colab's env for a live demo):
    USE_ML_MODEL=true
    HF_MODEL_REPO=<your-username>/sia-churn-model
    HF_MODEL_REVISION=v1.0.0
so backend/models/loader.py picks it up instead of falling back to the
formula.
"""

import json
import os
import sys

try:
    from huggingface_hub import HfApi, create_repo
except ImportError:
    sys.exit("huggingface_hub not installed -- run: pip install huggingface_hub")

TOKEN = os.environ.get("HF_TOKEN")
REPO_ID = os.environ.get("HF_MODEL_REPO")
ARTIFACT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "artifacts")
VERSION_TAG = "v1.0.0"

if not TOKEN:
    sys.exit("Set HF_TOKEN (a Hugging Face access token with write scope) before running this.")
if not REPO_ID:
    sys.exit("Set HF_MODEL_REPO (e.g. yourname/sia-churn-model) before running this.")

required = ["model.joblib", "feature_columns.json", "metrics.json", "MODEL_CARD.md"]
missing = [f for f in required if not os.path.exists(os.path.join(ARTIFACT_DIR, f))]
if missing:
    sys.exit(f"Missing {missing} in {ARTIFACT_DIR} -- run notebooks/02_train_model.py first.")

with open(os.path.join(ARTIFACT_DIR, "metrics.json")) as f:
    metrics = json.load(f)
test_row = metrics["splits"][-1]
print(
    f"About to publish a model with test ROC-AUC={test_row['model']['roc_auc']} "
    f"(old formula on the same rows: {test_row['old_formula_roc_auc']})"
)

api = HfApi(token=TOKEN)

print(f"Creating (or reusing) model repo {REPO_ID} ...")
create_repo(REPO_ID, token=TOKEN, repo_type="model", exist_ok=True)

for fname, dest in [
    ("model.joblib", "model.joblib"),
    ("feature_columns.json", "feature_columns.json"),
    ("metrics.json", "metrics.json"),
    ("MODEL_CARD.md", "README.md"),
]:
    print(f"Uploading {fname} -> {dest} ...")
    api.upload_file(
        path_or_fileobj=os.path.join(ARTIFACT_DIR, fname),
        path_in_repo=dest,
        repo_id=REPO_ID,
        repo_type="model",
    )

print(f"Tagging {VERSION_TAG} ...")
api.create_tag(REPO_ID, tag=VERSION_TAG, repo_type="model", exist_ok=True)

print(f"Done: https://huggingface.co/{REPO_ID}")
print(f"Set HF_MODEL_REPO={REPO_ID}, HF_MODEL_REVISION={VERSION_TAG}, USE_ML_MODEL=true in .env to use it.")
