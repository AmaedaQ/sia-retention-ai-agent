"""Loads the trained churn model from Hugging Face, with a safe fallback.

Phase 3: this is the real implementation the Phase 0 docstring promised.
Downloads and caches `model.joblib` + `feature_columns.json` from
`settings.hf_model_repo` at the pinned `settings.hf_model_revision` (never
"latest" silently -- a revision bump is a deliberate config change, not an
automatic one). While `USE_ML_MODEL=False`, or if the repo isn't
configured, or if the download/load fails for any reason, callers get
`ModelUnavailable` and are expected to fall back to the original
hand-written formula in agents/monitor.py -- the rest of the pipeline
never has to know which path served a prediction.
"""

import os
import sys
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import settings


class ModelUnavailable(Exception):
    """Raised when the ML model can't be loaded. Callers should catch this
    and fall back to the formula -- never let it crash the pipeline."""


class LoadedModel:
    """Bundles the classifier with the exact feature-column order it was
    trained on, and the revision tag it was loaded from -- so a prediction
    can always report which model version produced it (RiskPrediction's
    `model_revision` field)."""

    def __init__(self, model, feature_columns: list, revision: str):
        self.model = model
        self.feature_columns = feature_columns
        self.revision = revision


def load_churn_model() -> LoadedModel:
    """Downloads and caches the versioned model from Hugging Face.

    Raises ModelUnavailable (never a raw exception from huggingface_hub or
    joblib) so every caller has exactly one exception type to catch.
    """
    if not settings.use_ml_model:
        raise ModelUnavailable("USE_ML_MODEL is False -- using the formula.")
    if not settings.hf_model_repo:
        raise ModelUnavailable("HF_MODEL_REPO is not configured.")

    try:
        from huggingface_hub import hf_hub_download
        import joblib
        import json
    except ImportError as e:
        raise ModelUnavailable(f"missing dependency for model loading: {e}") from e

    try:
        model_path = hf_hub_download(
            repo_id=settings.hf_model_repo,
            filename="model.joblib",
            revision=settings.hf_model_revision,
        )
        columns_path = hf_hub_download(
            repo_id=settings.hf_model_repo,
            filename="feature_columns.json",
            revision=settings.hf_model_revision,
        )
    except Exception as e:  # noqa: BLE001 -- huggingface_hub raises several distinct error types
        raise ModelUnavailable(
            f"could not download model {settings.hf_model_repo}@{settings.hf_model_revision}: {e}"
        ) from e

    try:
        model = joblib.load(model_path)
        with open(columns_path) as f:
            feature_columns = json.load(f)
    except Exception as e:  # noqa: BLE001
        raise ModelUnavailable(f"could not load downloaded model files: {e}") from e

    return LoadedModel(model=model, feature_columns=feature_columns, revision=settings.hf_model_revision)


_cached_model: Optional[LoadedModel] = None
_load_attempted = False


def get_churn_model() -> LoadedModel:
    """Cached accessor -- loads once per process, not once per prediction.
    A failed load is cached too (as the raised exception, re-raised on
    every subsequent call) so a misconfigured repo doesn't retry a slow
    network call on every single request."""
    global _cached_model, _load_attempted
    if _cached_model is None:
        if _load_attempted:
            raise ModelUnavailable("model load already failed this process -- see the earlier error")
        _load_attempted = True
        _cached_model = load_churn_model()
    return _cached_model


def reset_model_cache():
    """Test/ops hook -- clears the cache so a config change (or a retry
    after fixing HF_MODEL_REPO) takes effect without restarting the
    process."""
    global _cached_model, _load_attempted
    _cached_model = None
    _load_attempted = False
