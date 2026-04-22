from typing import Any

from pydantic import BaseModel, Field


class IntegrationStatus(BaseModel):
    system_code: str
    system_name: str
    enabled: bool = True
    status: str = "connected"
    last_sync_at: str = ""
    owner: str = "platform"
    detail: dict[str, Any] = Field(default_factory=dict)


class UnifiedTaskRequest(BaseModel):
    task_type: str
    source_system: str
    target_system: str
    payload: dict[str, Any] = Field(default_factory=dict)


class UnifiedTaskResult(BaseModel):
    task_id: str
    task_type: str
    source_system: str
    target_system: str
    status: str
    message: str
    next_actions: list[str] = Field(default_factory=list)
    created_at: str = ""
