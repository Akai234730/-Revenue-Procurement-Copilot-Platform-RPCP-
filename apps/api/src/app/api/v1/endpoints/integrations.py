from dataclasses import asdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.identity import User
from app.schemas.common import APIResponse
from app.schemas.integration import UnifiedTaskRequest
from app.services.audit_service import AuditService
from app.services.integration_service import IntegrationService

router = APIRouter()
service = IntegrationService()


@router.get("/systems", response_model=APIResponse)
def list_systems(_: User = Depends(get_current_user)) -> APIResponse:
    items = service.list_integrations()
    return APIResponse(data=[asdict(item) for item in items])


@router.get("/tasks", response_model=APIResponse)
def list_tasks(_: User = Depends(get_current_user)) -> APIResponse:
    return APIResponse(data=[asdict(item) for item in service.list_tasks()])


@router.post("/tasks", response_model=APIResponse)
def create_unified_task(
    payload: UnifiedTaskRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    task = service.dispatch_task(
        task_type=payload.task_type,
        source_system=payload.source_system,
        target_system=payload.target_system,
        payload=payload.payload,
    )
    audit_service = AuditService(db)
    event = audit_service.build_event(
        module_name="integration",
        action_name="dispatch_task",
        operator_id=current_user.id,
        target_type="integration_task",
        target_id=task.task_id,
        result=task.status,
        detail={
            "task_type": task.task_type,
            "source_system": task.source_system,
            "target_system": task.target_system,
        },
    )
    audit_service.persist_event(event)
    db.commit()
    return APIResponse(data=asdict(task))
