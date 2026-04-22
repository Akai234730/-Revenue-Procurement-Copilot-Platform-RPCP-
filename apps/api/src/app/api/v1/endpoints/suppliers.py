from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.identity import User
from app.models.supplier import Supplier, SupplierEvaluation
from app.schemas.common import APIResponse
from app.schemas.domain_write import SupplierCreate, SupplierStatusUpdate, SupplierUpdate
from app.services.audit_service import AuditService

router = APIRouter()

_ALLOWED_SUPPLIER_STATUSES = {"active", "inactive", "suspended", "archived"}


def _dump(item):
    return {k: v for k, v in item.__dict__.items() if k != "_sa_instance_state"}


@router.get("", response_model=APIResponse)
def list_suppliers(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> APIResponse:
    items = db.query(Supplier).order_by(Supplier.updated_at.desc()).all()
    return APIResponse(data=[_dump(item) for item in items])


@router.post("", response_model=APIResponse)
def create_supplier(
    payload: SupplierCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    item = Supplier(
        supplier_name=payload.supplier_name,
        supplier_code=payload.supplier_code,
        supplier_category=payload.supplier_category,
        qualification_level=payload.qualification_level,
        region_code=payload.region_code,
        supplier_status="active",
    )
    db.add(item)
    db.flush()
    AuditService(db).persist_event(
        AuditService(db).build_event(
            module_name="supplier",
            action_name="create_supplier",
            operator_id=current_user.id,
            target_type="supplier",
            target_id=item.id,
            result="success",
            detail={"supplier_name": item.supplier_name},
        )
    )
    db.commit()
    db.refresh(item)
    return APIResponse(data={"id": item.id, "supplier_name": item.supplier_name})


@router.put("/{supplier_id}", response_model=APIResponse)
def update_supplier(
    supplier_id: str,
    payload: SupplierUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    item = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not item:
        raise AppError(code="SUPPLIER_NOT_FOUND", message="供应商不存在", status_code=404)

    updated_fields = payload.model_dump(exclude_none=True)
    target_status = str(updated_fields.get("supplier_status") or item.supplier_status or "active").strip().lower()
    if target_status not in _ALLOWED_SUPPLIER_STATUSES:
        raise AppError(code="SUPPLIER_STATUS_INVALID", message="供应商状态不合法", status_code=400)

    for field, value in updated_fields.items():
        if field == "supplier_status":
            setattr(item, field, target_status)
        else:
            setattr(item, field, value)

    AuditService(db).persist_event(
        AuditService(db).build_event(
            module_name="supplier",
            action_name="update_supplier",
            operator_id=current_user.id,
            target_type="supplier",
            target_id=item.id,
            result="success",
            detail={"updated_fields": list(updated_fields.keys())},
        )
    )
    db.commit()
    db.refresh(item)
    return APIResponse(data={"id": item.id, "supplier_status": item.supplier_status})


@router.post("/{supplier_id}/status", response_model=APIResponse)
def update_supplier_status(
    supplier_id: str,
    payload: SupplierStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    item = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not item:
        raise AppError(code="SUPPLIER_NOT_FOUND", message="供应商不存在", status_code=404)

    current_status = (item.supplier_status or "active").strip().lower()
    target_status = payload.supplier_status.strip().lower()
    if target_status not in _ALLOWED_SUPPLIER_STATUSES:
        raise AppError(code="SUPPLIER_STATUS_INVALID", message="供应商状态不合法", status_code=400)

    item.supplier_status = target_status
    AuditService(db).persist_event(
        AuditService(db).build_event(
            module_name="supplier",
            action_name="update_supplier_status",
            operator_id=current_user.id,
            target_type="supplier",
            target_id=item.id,
            result="success",
            detail={"from": current_status, "to": target_status},
        )
    )
    db.commit()
    db.refresh(item)
    return APIResponse(data={"id": item.id, "supplier_status": item.supplier_status})


@router.delete("/{supplier_id}", response_model=APIResponse)
def delete_supplier(
    supplier_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> APIResponse:
    item = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not item:
        raise AppError(code="SUPPLIER_NOT_FOUND", message="供应商不存在", status_code=404)

    evaluations = db.query(SupplierEvaluation).filter(SupplierEvaluation.supplier_id == supplier_id).all()
    for evaluation in evaluations:
        db.delete(evaluation)

    AuditService(db).persist_event(
        AuditService(db).build_event(
            module_name="supplier",
            action_name="delete_supplier",
            operator_id=current_user.id,
            target_type="supplier",
            target_id=item.id,
            result="success",
            detail={"supplier_name": item.supplier_name, "evaluation_count": len(evaluations)},
        )
    )
    db.delete(item)
    db.commit()
    return APIResponse(data={"id": supplier_id, "deleted": True})


@router.get("/evaluations", response_model=APIResponse)
def list_supplier_evaluations(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> APIResponse:
    items = db.query(SupplierEvaluation).order_by(SupplierEvaluation.updated_at.desc()).all()
    return APIResponse(data=[_dump(item) for item in items])


@router.get("/{supplier_id}", response_model=APIResponse)
def get_supplier(
    supplier_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> APIResponse:
    item = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not item:
        raise AppError(code="SUPPLIER_NOT_FOUND", message="供应商不存在", status_code=404)
    evaluations = db.query(SupplierEvaluation).filter(SupplierEvaluation.supplier_id == supplier_id).order_by(SupplierEvaluation.updated_at.desc()).all()
    return APIResponse(data={**_dump(item), "evaluations": [_dump(evaluation) for evaluation in evaluations]})
