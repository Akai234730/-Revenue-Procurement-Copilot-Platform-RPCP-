from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.common import APIResponse
from app.services.observability_service import ObservabilityService

router = APIRouter()


@router.get("", response_model=APIResponse)
def health_check(db: Session = Depends(get_db)) -> APIResponse:
    service = ObservabilityService(db)
    return APIResponse(data=service.runtime_status())


@router.get("/metrics", response_model=APIResponse)
def metrics(db: Session = Depends(get_db)) -> APIResponse:
    service = ObservabilityService(db)
    return APIResponse(data=service.metrics_overview())
