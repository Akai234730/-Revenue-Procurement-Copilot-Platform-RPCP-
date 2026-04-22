from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.identity import User
from app.models.lead import FollowupRecord, Lead
from app.schemas.common import APIResponse
from app.schemas.lead_write import FollowupCreate, LeadCreate, LeadStatusUpdate, LeadUpdate
from app.services.audit_service import AuditService

router = APIRouter()

_ALLOWED_STATUSES = {"new", "contacted", "qualified", "proposal", "won", "lost", "invalid", "archived"}


def _dump(item):
    return {k: v for k, v in item.__dict__.items() if k != "_sa_instance_state"}


@router.get("", response_model=APIResponse)
def list_leads(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> APIResponse:
    items = db.query(Lead).order_by(Lead.updated_at.desc()).all()
    return APIResponse(data=[_dump(item) for item in items])


@router.post("", response_model=APIResponse)
def create_lead(
    payload: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    lead = Lead(
        source_channel=payload.source_channel,
        source_detail=payload.source_detail,
        company_name=payload.company_name,
        contact_name=payload.contact_name,
        contact_title=payload.contact_title,
        phone=payload.phone,
        email=payload.email or "",
        industry_code=payload.industry_code,
        industry_name=payload.industry_name,
        company_size=payload.company_size,
        region_code=payload.region_code,
        website_url=payload.website_url,
        demand_summary=payload.demand_summary,
        budget_signal=payload.budget_signal,
        project_stage=payload.project_stage,
        owner_user_id=payload.owner_user_id or current_user.id,
        ai_profile_summary="待分析",
        ai_lead_score=0,
        ai_maturity_level="low",
        ai_priority_level="P3",
        ai_next_action="待生成",
        ai_confidence=0,
        ai_risk_flag="[]",
        lead_status="new",
        crm_sync_status="pending",
        invalid_reason="",
        archived=False,
    )
    db.add(lead)
    db.flush()
    AuditService(db).persist_event(
        AuditService(db).build_event(
            module_name="lead",
            action_name="create_lead",
            operator_id=current_user.id,
            target_type="lead",
            target_id=lead.id,
            result="success",
            detail={"company_name": lead.company_name},
        )
    )
    db.commit()
    db.refresh(lead)
    return APIResponse(data={"id": lead.id, "company_name": lead.company_name})


@router.get("/{lead_id}", response_model=APIResponse)
def get_lead(lead_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> APIResponse:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise AppError(code="LEAD_NOT_FOUND", message="线索不存在", status_code=404)
    followups = db.query(FollowupRecord).filter(FollowupRecord.lead_id == lead_id).order_by(FollowupRecord.created_at.desc()).all()
    return APIResponse(data={**_dump(lead), "followups": [_dump(item) for item in followups]})


@router.put("/{lead_id}", response_model=APIResponse)
def update_lead(
    lead_id: str,
    payload: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise AppError(code="LEAD_NOT_FOUND", message="线索不存在", status_code=404)

    updated_fields = payload.model_dump(exclude_none=True)
    target_status = str(updated_fields.get("lead_status") or lead.lead_status or "new").strip().lower()
    if target_status not in _ALLOWED_STATUSES:
        raise AppError(code="LEAD_STATUS_INVALID", message="线索状态不合法", status_code=400)

    for field, value in updated_fields.items():
        if field == "lead_status":
            setattr(lead, field, target_status)
        else:
            setattr(lead, field, value)

    lead.archived = target_status == "archived"
    if target_status != "invalid":
        lead.invalid_reason = updated_fields.get("invalid_reason", "") or ""

    AuditService(db).persist_event(
        AuditService(db).build_event(
            module_name="lead",
            action_name="update_lead",
            operator_id=current_user.id,
            target_type="lead",
            target_id=lead.id,
            result="success",
            detail={"updated_fields": list(updated_fields.keys())},
        )
    )
    db.commit()
    db.refresh(lead)
    return APIResponse(data={"id": lead.id, "lead_status": lead.lead_status})


@router.post("/{lead_id}/status", response_model=APIResponse)
def update_lead_status(
    lead_id: str,
    payload: LeadStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise AppError(code="LEAD_NOT_FOUND", message="线索不存在", status_code=404)

    target_status = payload.lead_status.strip().lower()
    current_status = (lead.lead_status or "new").strip().lower()
    if target_status not in _ALLOWED_STATUSES:
        raise AppError(code="LEAD_STATUS_INVALID", message="线索状态不合法", status_code=400)

    lead.lead_status = target_status
    lead.archived = target_status == "archived"
    lead.invalid_reason = payload.invalid_reason if target_status == "invalid" else ""

    AuditService(db).persist_event(
        AuditService(db).build_event(
            module_name="lead",
            action_name="update_lead_status",
            operator_id=current_user.id,
            target_type="lead",
            target_id=lead.id,
            result="success",
            detail={"from": current_status, "to": target_status, "invalid_reason": payload.invalid_reason},
        )
    )
    db.commit()
    db.refresh(lead)
    return APIResponse(data={"id": lead.id, "lead_status": lead.lead_status, "archived": lead.archived})


@router.post("/{lead_id}/sync-crm", response_model=APIResponse)
def sync_lead_to_crm(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise AppError(code="LEAD_NOT_FOUND", message="线索不存在，无法写入客户管理系统", status_code=404)

    lead.crm_sync_status = "synced"

    AuditService(db).persist_event(
        AuditService(db).build_event(
            module_name="lead",
            action_name="sync_lead_to_crm",
            operator_id=current_user.id,
            target_type="lead",
            target_id=lead.id,
            result="success",
            detail={"company_name": lead.company_name, "crm_sync_status": lead.crm_sync_status},
        )
    )
    db.commit()
    db.refresh(lead)
    return APIResponse(data={"id": lead.id, "crm_sync_status": lead.crm_sync_status})


@router.delete("/{lead_id}", response_model=APIResponse)
def delete_lead(
    lead_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise AppError(code="LEAD_NOT_FOUND", message="线索不存在", status_code=404)

    followups = db.query(FollowupRecord).filter(FollowupRecord.lead_id == lead_id).all()
    for followup in followups:
        db.delete(followup)

    AuditService(db).persist_event(
        AuditService(db).build_event(
            module_name="lead",
            action_name="delete_lead",
            operator_id=current_user.id,
            target_type="lead",
            target_id=lead.id,
            result="success",
            detail={"company_name": lead.company_name, "followup_count": len(followups)},
        )
    )
    db.delete(lead)
    db.commit()
    return APIResponse(data={"id": lead_id, "deleted": True})


@router.post("/{lead_id}/followups", response_model=APIResponse)
def create_followup(
    lead_id: str,
    payload: FollowupCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise AppError(code="LEAD_NOT_FOUND", message="线索不存在，无法创建跟进记录", status_code=404)
    followup = FollowupRecord(
        lead_id=lead_id,
        followup_type=payload.followup_type,
        followup_channel=payload.followup_channel,
        followup_content=payload.followup_content,
        followup_result=payload.followup_result,
        next_action=payload.next_action,
        recorder_user_id=current_user.id,
        ai_generated_flag=False,
    )
    db.add(followup)
    db.flush()

    normalized_result = (payload.followup_result or "").strip().lower()
    if normalized_result in _ALLOWED_STATUSES - {"new", "archived"}:
        lead.lead_status = normalized_result
        lead.archived = False
        if normalized_result == "invalid" and payload.next_action:
            lead.invalid_reason = payload.next_action
        elif normalized_result != "invalid":
            lead.invalid_reason = ""

    AuditService(db).persist_event(
        AuditService(db).build_event(
            module_name="lead",
            action_name="create_followup",
            operator_id=current_user.id,
            target_type="followup",
            target_id=followup.id,
            result="success",
            detail={"lead_id": lead_id, "followup_result": payload.followup_result},
        )
    )
    db.commit()
    db.refresh(followup)
    return APIResponse(data={"id": followup.id, "lead_id": followup.lead_id})
