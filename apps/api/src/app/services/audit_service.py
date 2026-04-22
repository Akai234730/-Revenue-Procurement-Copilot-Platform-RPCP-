from dataclasses import dataclass
from typing import Any

from sqlalchemy.orm import Session

from app.models.platform import AuditLog


@dataclass(slots=True)
class AuditEvent:
    module_name: str
    action_name: str
    operator_id: str
    target_type: str
    target_id: str
    result: str
    detail: dict[str, Any]


class AuditService:
    def __init__(self, db: Session | None = None):
        self.db = db

    def build_event(
        self,
        module_name: str,
        action_name: str,
        operator_id: str,
        target_type: str,
        target_id: str,
        result: str,
        detail: dict[str, Any],
    ) -> AuditEvent:
        return AuditEvent(
            module_name=module_name,
            action_name=action_name,
            operator_id=operator_id,
            target_type=target_type,
            target_id=target_id,
            result=result,
            detail=detail,
        )

    def persist_event(self, event: AuditEvent) -> AuditLog | None:
        if not self.db:
            return None
        log = AuditLog(
            module_name=event.module_name,
            action_name=event.action_name,
            operator_id=event.operator_id,
            target_type=event.target_type,
            target_id=event.target_id,
            result=event.result,
            detail=str(event.detail),
        )
        self.db.add(log)
        self.db.flush()
        return log
