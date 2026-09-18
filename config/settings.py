"""Central configuration for SIA. Reads from environment / .env; every
setting has a safe default so the app still runs with nothing configured
(falling back to the original heuristic scoring, phase 3+)."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

_env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
if os.path.exists(_env_path):
    load_dotenv(_env_path)


def _get_bool(name: str, default: bool) -> bool:
    val = os.getenv(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class Settings:
    # --- Reasoning layer (unchanged from the original project) ---
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # --- ML risk-scoring layer (added for the model-upgrade phases) ---
    # When False, monitor.py uses the original hand-written formula. This
    # is the rollback switch: flip it off if the trained model is ever
    # unavailable or misbehaving, with zero code changes required.
    use_ml_model: bool = _get_bool("USE_ML_MODEL", False)

    # Hugging Face repo the trained model is published to (Phase 2), and
    # the exact revision/tag to pin (never load "latest" silently).
    hf_model_repo: str = os.getenv("HF_MODEL_REPO", "")
    hf_model_revision: str = os.getenv("HF_MODEL_REVISION", "v1.0.0")

    # Decision threshold for flagging a subscriber as high-risk. Kept
    # separate from the model itself so it can be tuned without retraining.
    churn_risk_threshold: float = float(os.getenv("CHURN_RISK_THRESHOLD", "0.7"))

    # How many top SHAP factors to surface to the Decider agent's prompt.
    shap_top_k: int = int(os.getenv("SHAP_TOP_K", "3"))


settings = Settings()
