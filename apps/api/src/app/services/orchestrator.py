from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from app.services.ai_provider import AIProviderError, ProviderRequest
from app.services.mock_ai_provider import MockAIProvider
from app.services.provider_registry import get_ai_provider


@dataclass(slots=True)
class AgentTask:
    task_id: str
    agent_name: str
    scene: str
    provider: str
    status: str = "queued"
    summary: str = ""
    context: dict[str, Any] = field(default_factory=dict)
    steps: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    insights: list[dict[str, Any]] = field(default_factory=list)
    next_actions: list[str] = field(default_factory=list)
    raw_output: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None
    duration_ms: int = 0
    degraded: bool = False
    error_message: str = ""


class AgentOrchestratorService:
    def _mapping(self) -> dict[str, dict[str, Any]]:
        return {
            "lead_followup": {
                "agent_name": "lead_followup_agent",
                "steps": ["collect_customer_context", "score_opportunity", "generate_followup_script", "audit_record"],
            },
            "proposal_generation": {
                "agent_name": "proposal_generation_agent",
                "steps": ["parse_rfp", "retrieve_knowledge", "draft_solution", "compliance_review"],
            },
            "supplier_assessment": {
                "agent_name": "supplier_assessment_agent",
                "steps": ["collect_supplier_profile", "score_dimensions", "assess_risks", "generate_cooperation_advice"],
            },
            "procurement_analysis": {
                "agent_name": "procurement_analysis_agent",
                "steps": ["normalize_requirements", "compare_quotes", "score_suppliers", "generate_recommendation"],
            },
            "ops_analysis": {
                "agent_name": "ops_copilot_agent",
                "steps": ["collect_runtime_metrics", "evaluate_quality", "detect_anomaly", "suggest_optimization"],
            },
        }

    def build_task(self, agent_name: str, scene: str, provider: str, context: dict[str, Any], steps: list[str]) -> AgentTask:
        timestamp = datetime.now(UTC).strftime('%Y%m%d%H%M%S')
        return AgentTask(
            task_id=f"task_{agent_name}_{timestamp}",
            agent_name=agent_name,
            scene=scene,
            provider=provider,
            context=context,
            steps=steps,
        )

    def prepare_task(self, scene: str, entity_id: str | None, context: dict[str, Any]) -> AgentTask:
        selected = self._mapping().get(scene, self._mapping()["ops_analysis"])
        provider = get_ai_provider()
        return self.build_task(
            agent_name=selected["agent_name"],
            scene=scene,
            provider=provider.provider_name,
            context={"entity_id": entity_id, **context},
            steps=selected["steps"],
        )

    def execute_task(self, task: AgentTask, entity_id: str | None, context: dict[str, Any]) -> AgentTask:
        provider = get_ai_provider()
        started_at = datetime.now(UTC)
        task.status = "running"
        task.context = {"entity_id": entity_id, **context}
        try:
            provider_result = provider.execute(ProviderRequest(scene=task.scene, entity_id=entity_id, context=context))
            task.status = "completed"
            task.raw_output = provider_result.raw_output
            task.summary = provider_result.summary
            task.recommendations = provider_result.recommendations
            task.evidence = provider_result.evidence
            task.next_actions = provider_result.next_actions
            task.insights = provider_result.insights
        except AIProviderError as exc:
            task.error_message = str(exc)
            if exc.allow_fallback:
                fallback = MockAIProvider()
                provider_result = fallback.execute(ProviderRequest(scene=task.scene, entity_id=entity_id, context=context))
                task.status = "degraded"
                task.degraded = True
                task.provider = f"{provider.provider_name}->mock"
                task.raw_output = {"error": str(exc), "fallback": "mock"}
                task.summary = provider_result.summary
                task.recommendations = provider_result.recommendations
                task.evidence = provider_result.evidence
                task.next_actions = provider_result.next_actions
                task.insights = provider_result.insights
            else:
                task.status = "failed"
                task.raw_output = {"error": str(exc), "fallback": "disabled"}
        task.completed_at = datetime.now(UTC)
        task.duration_ms = int((task.completed_at - started_at).total_seconds() * 1000)
        return task
