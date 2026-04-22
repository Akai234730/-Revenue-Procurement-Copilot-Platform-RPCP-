from datetime import UTC, datetime

from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.platform import AITaskExecution, AuditLog
from app.services.integration_service import IntegrationService


class ObservabilityService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def runtime_status(self) -> dict:
        integration_service = IntegrationService()
        systems = integration_service.list_integrations()
        return {
            "service": "rpcp-api",
            "environment": self.settings.app_env,
            "version": "0.1.0",
            "status": "ok",
            "timestamp": datetime.now(UTC).isoformat(),
            "provider": self.settings.ai_provider,
            "model_name": self.settings.ai_model_name,
            "database": "connected",
            "integrations": {
                "total": len(systems),
                "connected": len([item for item in systems if item.status == "connected"]),
                "warning": len([item for item in systems if item.status == "warning"]),
            },
        }

    def metrics_overview(self) -> dict:
        integration_count = len(IntegrationService().list_tasks())
        try:
            ai_count = self.db.query(AITaskExecution).count()
            degraded_count = self.db.query(AITaskExecution).filter(AITaskExecution.status == "degraded").count()
            audit_count = self.db.query(AuditLog).count()
        except ProgrammingError:
            self.db.rollback()
            ai_count = 0
            degraded_count = 0
            audit_count = 0
        return {
            "request_count": ai_count + audit_count + integration_count,
            "error_count": 0,
            "degraded_count": degraded_count,
            "ai_task_count": ai_count,
            "integration_task_count": integration_count,
            "audit_log_count": audit_count,
        }
