from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.platform import KnowledgeDocument
from app.schemas.common import APIResponse
from app.services.knowledge_service import KnowledgeService

router = APIRouter()


@router.get("/documents", response_model=APIResponse)
def list_documents(db: Session = Depends(get_db)) -> APIResponse:
    items = db.query(KnowledgeDocument).order_by(KnowledgeDocument.updated_at.desc()).all()
    return APIResponse(data=[{k: v for k, v in item.__dict__.items() if k != "_sa_instance_state"} for item in items])


@router.get("/search", response_model=APIResponse)
def search_knowledge(scene: str = Query(default="ops_analysis"), limit: int = Query(default=3), db: Session = Depends(get_db)) -> APIResponse:
    return APIResponse(data=KnowledgeService(db).retrieve_sources(scene=scene, limit=limit))
