from typing import Any

from pydantic import BaseModel, Field


class RuntimeStatus(BaseModel):
    service: str
    environment: str
    version: str
    status: str
    timestamp: str
    provider: str
    model_name: str
    database: str
    integrations: dict[str, Any] = Field(default_factory=dict)


class MetricsOverview(BaseModel):
    request_count: int = 0
    error_count: int = 0
    degraded_count: int = 0
    ai_task_count: int = 0
    integration_task_count: int = 0
    audit_log_count: int = 0
