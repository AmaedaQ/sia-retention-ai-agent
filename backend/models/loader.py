"""Loads the trained churn model from Hugging Face, with a safe fallback.

This is the Phase 0 interface only. Until Phase 2 publishes a real model to
`settings.hf_model_repo`, or while `USE_ML_MODEL=False`, every call here
falls back to the original hand-written formula in agents/monitor.py — the
rest of the pipeline never has to know which path served a prediction.
"""

import sys
import os
from typing import Optional

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config.settings import settings


class ModelUnavailable(Exception):
    """Raised when the ML model can't be loaded. Callers should catch this
    and fall back to the formula — never let it crash the pipeline."""


def load_churn_model():
    """Downloads and caches the versioned model from Hugging Face.

    Phase 0: intentionally unimplemented (raises ModelUnavailable) — there
    is no trained model yet. Phase 3 replaces the body of this function
    with a real `huggingface_hub.hf_hub_download` + deserialize call,
    pinned to `settings.hf_model_revision`. The signature and the
    fallback contract are decided now so Phase 3 is a pure swap-in.
    """
    if not settings.use_ml_model:
        raise ModelUnavailable("USE_ML_MODEL is False — using the formula.")
    if not settings.hf_model_repo:
        raise ModelUnavailable("HF_MODEL_REPO is not configured.")
    raise ModelUnavailable(
        "No trained model published yet (Phase 2 not complete). "
        "Falling back to the heuristic formula."
    )


_cached_model: Optional[object] = None


def get_churn_model():
    """Cached accessor — loads once per process, not once per prediction."""
    global _cached_model
    if _cached_model is None:
        _cached_model = load_churn_model()
    return _cached_model
