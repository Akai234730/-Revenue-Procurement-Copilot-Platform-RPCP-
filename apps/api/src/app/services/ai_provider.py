from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ProviderRequest:
    scene: str
    entity_id: str | None = None
    context: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProviderResult:
    summary: str
    recommendations: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    insights: list[dict[str, Any]] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    raw_output: dict[str, Any] = field(default_factory=dict)


class AIProviderError(Exception):
    def __init__(self, message: str, *, retryable: bool = True, allow_fallback: bool = False):
        super().__init__(message)
        self.retryable = retryable
        self.allow_fallback = allow_fallback


class AIProvider:
    provider_name = "base"

    def execute(self, request: ProviderRequest) -> ProviderResult:
        raise NotImplementedError
