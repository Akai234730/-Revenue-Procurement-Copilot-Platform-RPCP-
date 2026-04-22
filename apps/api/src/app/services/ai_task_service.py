import json
from threading import Lock
from typing import Any

from sqlalchemy.orm import Session

from app.models.platform import AITaskExecution
from app.services.orchestrator import AgentTask

_RUNTIME_TASKS: dict[str, dict[str, Any]] = {}
_RUNTIME_LOCK = Lock()


class AITaskService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def serialize_task(task: AgentTask) -> dict[str, Any]:
        return {
            "task_id": task.task_id,
            "scene": task.scene,
            "agent_name": task.agent_name,
            "provider": task.provider,
            "status": task.status,
            "summary": task.summary,
            "recommendations": task.recommendations,
            "evidence": task.evidence,
            "insights": task.insights,
            "next_actions": task.next_actions,
            "raw_output": task.raw_output,
            "context": task.context,
            "degraded": task.degraded,
            "error_message": task.error_message,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "duration_ms": task.duration_ms,
        }

    @staticmethod
    def upsert_runtime(task: AgentTask) -> dict[str, Any]:
        payload = AITaskService.serialize_task(task)
        with _RUNTIME_LOCK:
            _RUNTIME_TASKS[task.task_id] = payload
        return payload

    @staticmethod
    def get_runtime(task_id: str) -> dict[str, Any] | None:
        with _RUNTIME_LOCK:
            return _RUNTIME_TASKS.get(task_id)

    def persist_execution(self, task: AgentTask, operator_id: str, entity_id: str | None) -> AITaskExecution:
        record = AITaskExecution(
            task_id=task.task_id,
            scene=task.scene,
            agent_name=task.agent_name,
            provider=task.provider,
            operator_id=operator_id,
            entity_id=entity_id or "",
            status=task.status,
            summary=task.summary,
            recommendations=json.dumps(task.recommendations, ensure_ascii=False),
            evidence=json.dumps(task.evidence, ensure_ascii=False),
            insights=json.dumps(task.insights, ensure_ascii=False),
            next_actions=json.dumps(task.next_actions, ensure_ascii=False),
            context=json.dumps(task.context, ensure_ascii=False),
            raw_output=json.dumps(task.raw_output, ensure_ascii=False),
        )
        self.db.add(record)
        self.db.flush()
        self.db.refresh(record)
        return record

    def list_executions(self, limit: int = 20) -> list[AITaskExecution]:
        return self.db.query(AITaskExecution).order_by(AITaskExecution.created_at.desc()).limit(limit).all()

    def get_execution(self, task_id: str) -> AITaskExecution | None:
        return self.db.query(AITaskExecution).filter(AITaskExecution.task_id == task_id).first()
