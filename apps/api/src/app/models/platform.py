from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class KnowledgeDocument(BaseEntity):
    __tablename__ = "knowledge_documents"

    doc_name: Mapped[str] = mapped_column(String(255))
    doc_type: Mapped[str] = mapped_column(String(64), default="document")
    domain_type: Mapped[str] = mapped_column(String(64), default="general")
    source_system: Mapped[str] = mapped_column(String(64), default="manual")
    version_no: Mapped[str] = mapped_column(String(32), default="v1")
    owner_dept: Mapped[str] = mapped_column(String(128), default="")
    tags: Mapped[str] = mapped_column(Text, default="[]")
    permission_scope: Mapped[str] = mapped_column(String(128), default="internal")
    vector_status: Mapped[str] = mapped_column(String(32), default="pending")
    effective_date: Mapped[str] = mapped_column(String(32), default="")
    expire_date: Mapped[str] = mapped_column(String(32), default="")
    quality_score: Mapped[str] = mapped_column(String(16), default="0")


class AuditLog(BaseEntity):
    __tablename__ = "audit_logs"

    module_name: Mapped[str] = mapped_column(String(64), default="system")
    action_name: Mapped[str] = mapped_column(String(128), default="")
    operator_id: Mapped[str] = mapped_column(String(64), default="system")
    target_type: Mapped[str] = mapped_column(String(64), default="")
    target_id: Mapped[str] = mapped_column(String(64), default="")
    result: Mapped[str] = mapped_column(String(32), default="success")
    detail: Mapped[str] = mapped_column(Text, default="{}")


class AITaskExecution(BaseEntity):
    __tablename__ = "ai_task_executions"

    task_id: Mapped[str] = mapped_column(String(128), unique=True)
    scene: Mapped[str] = mapped_column(String(64), default="")
    agent_name: Mapped[str] = mapped_column(String(128), default="")
    provider: Mapped[str] = mapped_column(String(64), default="mock")
    operator_id: Mapped[str] = mapped_column(String(64), default="system")
    entity_id: Mapped[str] = mapped_column(String(64), default="")
    status: Mapped[str] = mapped_column(String(32), default="completed")
    summary: Mapped[str] = mapped_column(Text, default="")
    recommendations: Mapped[str] = mapped_column(Text, default="[]")
    evidence: Mapped[str] = mapped_column(Text, default="[]")
    insights: Mapped[str] = mapped_column(Text, default="[]")
    next_actions: Mapped[str] = mapped_column(Text, default="[]")
    context: Mapped[str] = mapped_column(Text, default="{}")
    raw_output: Mapped[str] = mapped_column(Text, default="{}")
