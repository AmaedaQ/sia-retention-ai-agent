"""Phase 0 tests: the data contracts reject bad data the way the pipeline
will depend on later. Run with: pytest tests/"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from pydantic import ValidationError

from backend.schemas import Subscriber, RiskPrediction, RetentionReport, SHAPFactor


def test_subscriber_valid():
    s = Subscriber(
        user_id="JAZZ_0001",
        avg_monthly_spend=1200.5,
        data_usage_gb=10.2,
        days_since_last_recharge=5,
        signal_strength_score=0.8,
        active_plan="Weekly Mega",
        support_tickets_open=0,
    )
    assert s.user_id == "JAZZ_0001"


def test_subscriber_rejects_blank_id():
    with pytest.raises(ValidationError):
        Subscriber(
            user_id="   ",
            avg_monthly_spend=100,
            data_usage_gb=1,
            days_since_last_recharge=1,
            signal_strength_score=0.5,
            active_plan="Daily Social",
            support_tickets_open=0,
        )


def test_subscriber_rejects_out_of_range_signal():
    with pytest.raises(ValidationError):
        Subscriber(
            user_id="JAZZ_0002",
            avg_monthly_spend=100,
            data_usage_gb=1,
            days_since_last_recharge=1,
            signal_strength_score=1.5,  # out of [0, 1]
            active_plan="Daily Social",
            support_tickets_open=0,
        )


def test_risk_prediction_requires_known_source():
    with pytest.raises(ValidationError):
        RiskPrediction(user_id="JAZZ_0001", churn_risk_score=0.9, source="guess")


def test_risk_prediction_formula_source_is_valid():
    p = RiskPrediction(user_id="JAZZ_0001", churn_risk_score=0.9, source="formula")
    assert p.top_factors == []


def test_retention_report_rejects_unknown_offer():
    with pytest.raises(ValidationError):
        RetentionReport(user_id="JAZZ_0001", reasoning="test", offer="Free Phone")


def test_retention_report_accepts_known_offer():
    r = RetentionReport(user_id="JAZZ_0001", reasoning="High risk", offer="Magic Bundle")
    assert r.offer == "Magic Bundle"


def test_shap_factor_shape():
    f = SHAPFactor(feature="days_since_last_recharge", value=40, impact=0.23)
    assert f.impact > 0
