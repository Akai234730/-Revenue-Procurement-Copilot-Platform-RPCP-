from typing import Any

from pydantic import BaseModel, Field


class AIExecuteRequest(BaseModel):
    scene: str = Field(..., description="业务场景，如 lead_followup/proposal_generation/procurement_analysis")
    entity_id: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)


class AIInsight(BaseModel):
    title: str
    content: str
    confidence: float = 0.0


class AIExecutionResult(BaseModel):
    task_id: str
    scene: str
    agent_name: str
    provider: str
    status: str
    summary: str
    recommendations: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    insights: list[AIInsight] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    raw_output: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    degraded: bool = False
    error_message: str = ""
    created_at: str | None = None
    completed_at: str | None = None
    duration_ms: int = 0


class AIHistoryItem(BaseModel):
    task_id: str
    scene: str
    agent_name: str
    provider: str
    operator_id: str
    entity_id: str
    status: str
    summary: str
    created_at: Any
