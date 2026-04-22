from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.session import get_db
from app.models.identity import User
from app.models.platform import AuditLog
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/logs", response_model=APIResponse)
def list_audit_logs(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> APIResponse:
    items = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(50).all()
    return APIResponse(
        data=[
            {
                "id": item.id,
                "module_name": item.module_name,
                "action_name": item.action_name,
                "operator_id": item.operator_id,
                "target_type": item.target_type,
                "target_id": item.target_id,
                "result": item.result,
                "detail": item.detail,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in items
        ]
    )
