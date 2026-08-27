"""Strict Pydantic contracts for inputs, outputs, and evaluation."""
from __future__ import annotations

import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


CategoryType = Literal[
    "Bug",
    "Feature Request",
    "How-To",
    "Performance",
    "Billing",
    "Integration",
    "Onboarding",
    "Data Loss",
]

UrgencyType = Literal["P1", "P2", "P3", "P4"]
PlanTierType = Literal["Starter", "Professional", "Business", "Enterprise"]
HealthStatusType = Literal["Healthy", "At Risk", "Churning", "New"]
UsageTrendType = Literal["Increasing", "Stable", "Declining", "Inactive"]


class TicketInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str | None = None
    body: str | None = None
    company: str | None = None
    account_id: str | None = None
    product: str | None = None
    plan_tier: str | None = None

    @field_validator("subject", "body", "company", "account_id", "product", "plan_tier")
    @classmethod
    def clean_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    @model_validator(mode="after")
    def require_content(self) -> "TicketInput":
        if not (self.subject or self.body):
            raise ValueError("At least subject or body must contain usable text.")
        return self


class TriageResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product: str
    product_area: str
    category: CategoryType
    urgency: UrgencyType
    urgency_reasoning: str
    is_known_issue: bool
    matched_kb_document: str | None = None
    matched_kb_section: str | None = None
    kb_resolution_steps: str | None = None
    recommended_team: str
    draft_response: str
    secondary_topics: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)
    kb_retrieval_score: float | None = Field(default=None, ge=0.0, le=1.0)


class FlaggedRiskItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    risk_title: str
    severity: Literal["High", "Medium", "Low"]
    signal_source: Literal["ticket", "escalation_note", "usage_metric", "contract"]
    quote_or_evidence: str
    ticket_id: str | None = None


class AccountHealthBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

    account_id: str
    company: str
    tam_name: str
    plan_tier: PlanTierType | None = None
    arr_usd: int | None = Field(default=None, ge=0)
    health_status: HealthStatusType | None = None
    usage_trend: UsageTrendType | None = None
    executive_summary: str
    open_risks_and_flags: list[FlaggedRiskItem] = Field(default_factory=list)
    recommended_talking_points: list[str] = Field(default_factory=list)
    metrics_snapshot: dict[str, Any] = Field(default_factory=dict)
    data_quality_warnings: list[str] = Field(default_factory=list)

    @field_validator("executive_summary")
    @classmethod
    def validate_summary(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Executive summary cannot be empty.")
        count = len(
            [s for s in re.split(r"(?<=[.!?])\s+", value) if s.strip()]
        )
        if not 3 <= count <= 5:
            raise ValueError(
                f"Executive summary must contain 3-5 sentences; got {count}."
            )
        return value


class TestCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    test_id: str
    task: Literal["task_1_triage", "task_2_account_health"]
    name: str
    is_adversarial: bool = False
    input_data: dict[str, Any]
    expected_criteria: dict[str, Any]


class SingleEvalResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    test_id: str
    task: str
    name: str
    is_adversarial: bool
    passed: bool
    quality_score: float = Field(ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)
    actual_output: dict[str, Any]
    latency_ms: float = Field(ge=0.0)


class EvalReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    timestamp: str
    total_tests: int = Field(ge=0)
    passed_tests: int = Field(ge=0)
    failed_tests: int = Field(ge=0)
    overall_pass_rate: float = Field(ge=0.0, le=1.0)
    average_quality_score: float = Field(ge=0.0, le=1.0)
    task_1_pass_rate: float = Field(ge=0.0, le=1.0)
    task_2_pass_rate: float = Field(ge=0.0, le=1.0)
    results: list[SingleEvalResult] = Field(default_factory=list)
