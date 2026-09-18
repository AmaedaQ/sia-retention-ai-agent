"""Type-safe contracts for everything that crosses an agent boundary.

Phase 0 goal: pin these shapes down *before* Phase 1-3 touch real data or a
trained model, so a bad row or a bad model output fails fast and loud here
instead of silently corrupting a downstream agent's state.
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class Subscriber(BaseModel):
    """One row of subscriber data, whether it came from the synthetic
    generator (today) or the real dataset pipeline (Phase 1)."""

    user_id: str
    avg_monthly_spend: float = Field(ge=0)
    data_usage_gb: float = Field(ge=0)
    days_since_last_recharge: int = Field(ge=0)
    signal_strength_score: float = Field(ge=0, le=1)
    active_plan: str
    support_tickets_open: int = Field(ge=0)
    churn_risk_score: Optional[float] = Field(default=None, ge=0, le=1)

    @field_validator("user_id")
    @classmethod
    def user_id_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("user_id must not be blank")
        return v


class SHAPFactor(BaseModel):
    """One feature's contribution to a single prediction, in plain terms
    the Decider agent's prompt can quote directly."""

    feature: str
    value: float
    impact: float  # signed SHAP value: positive = pushes risk up


class RiskPrediction(BaseModel):
    """What the Monitor agent produces for one subscriber, regardless of
    whether the score came from the ML model (Phase 3+) or the original
    hand-written formula (the fallback path)."""

    user_id: str
    churn_risk_score: float = Field(ge=0, le=1)
    source: str = Field(description='"model" or "formula"')
    model_revision: Optional[str] = None
    top_factors: list[SHAPFactor] = Field(default_factory=list)

    @field_validator("source")
    @classmethod
    def source_known(cls, v: str) -> str:
        if v not in ("model", "formula"):
            raise ValueError('source must be "model" or "formula"')
        return v


class RetentionReport(BaseModel):
    """One row of the Decider agent's output — already close to
    decider.py's existing JSON shape, just validated."""

    user_id: str
    reasoning: str
    offer: str

    @field_validator("offer")
    @classmethod
    def offer_known(cls, v: str) -> str:
        allowed = {"Magic Bundle", "Network Discount", "Recharge Bonus"}
        if v not in allowed:
            raise ValueError(f"offer must be one of {sorted(allowed)}, got {v!r}")
        return v


class AgentState(BaseModel):
    """Mirrors graph.py's TypedDict AgentState, as a validated schema for
    tests and for anything (like a notebook) that builds state outside the
    LangGraph runtime itself. graph.py keeps its TypedDict — LangGraph
    needs that — this is the contract the TypedDict is promising to keep."""

    threshold: float = Field(default=0.7, ge=0, le=1)
    risky_users: list[Subscriber] = Field(default_factory=list)
    final_reports: list[RetentionReport] = Field(default_factory=list)
