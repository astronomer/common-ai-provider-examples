from pydantic import BaseModel, Field
from typing import Literal


class SeverityReport(BaseModel):
    severity: Literal["low", "medium", "high", "critical"]
    summary: str
    affected_systems: list[str]
    recommended_action: str


class CargoDecision(BaseModel):
    lane: Literal["fast_lane", "customs_review", "quarantine"]
    reason: str
    risk_score: float = Field(ge=0.0, le=1.0)


class MissionPlan(BaseModel):
    mission_name: str
    origin: str
    destination: str
    steps: list[str]
    estimated_days: float


class AnomalyFinding(BaseModel):
    anomaly_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    notes: str


class FileAnalysisReport(BaseModel):
    title: str
    findings: list[AnomalyFinding]


class RouteAnswer(BaseModel):
    question: str
    top_routes: list[str]
    rationale: str
