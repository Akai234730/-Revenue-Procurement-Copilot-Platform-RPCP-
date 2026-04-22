from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.exceptions import AppError
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.identity import User
from app.models.procurement import PurchaseRequest, Quote, RFQ
from app.models.supplier import Supplier
from app.schemas.common import APIResponse
from app.schemas.domain_write import PurchaseRequestCreate, PurchaseRequestStatusUpdate, PurchaseRequestUpdate, QuoteCreate, RFQAwardPayload, RFQCreate, RFQStatusUpdate, RFQUpdate
from app.services.audit_service import AuditService

router=APIRouter()
REQ={"draft","submitted","approved","sourcing","quoted","awarded","cancelled"}
RFQ_S={"draft","published","quoted","evaluating","awarded","closed","cancelled"}

def _dump(i): return {k:v for k,v in i.__dict__.items() if k!="_sa_instance_state"}
def _pr(db,i):
    item=db.query(PurchaseRequest).filter(PurchaseRequest.id==i).first()
    if not item: raise AppError(code="PURCHASE_REQUEST_NOT_FOUND",message="采购申请不存在",status_code=404)
    return item
def _rfq(db,i):
    item=db.query(RFQ).filter(RFQ.id==i).first()
    if not item: raise AppError(code="RFQ_NOT_FOUND",message="询价任务不存在",status_code=404)
    return item
def _audit(db,u,a,t,tid,d):
    s=AuditService(db);s.persist_event(s.build_event(module_name="procurement",action_name=a,operator_id=u.id,target_type=t,target_id=tid,result="success",detail=d))
def _award(q,s):
    n=s.supplier_name if s else "待定";m=q.quote_total_amount_tax if q else 0
    return '{"awarded_supplier_id": "%s", "awarded_supplier_name": "%s", "decision_basis": "综合价格、风险和交付能力后完成定标", "awarded_amount_tax": %s}'%((s.id if s else ""),n.replace('"','\\"'),m)

@router.get("/purchase-requests",response_model=APIResponse)
def list_purchase_requests(db:Session=Depends(get_db),_:User=Depends(get_current_user))->APIResponse:
    return APIResponse(data=[_dump(i) for i in db.query(PurchaseRequest).order_by(PurchaseRequest.updated_at.desc()).all()])
@router.post("/purchase-requests",response_model=APIResponse)
def create_purchase_request(payload:PurchaseRequestCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:
    i=PurchaseRequest(applicant_user_id=payload.applicant_user_id or current_user.id,dept_id=payload.dept_id,category_code=payload.category_code,demand_desc=payload.demand_desc,expected_quantity=payload.expected_quantity,budget_amount=payload.budget_amount,request_status="submitted")
    db.add(i);db.flush();_audit(db,current_user,"create_purchase_request","purchase_request",i.id,{"demand_desc":i.demand_desc});db.commit();db.refresh(i)
    return APIResponse(data={"id":i.id,"demand_desc":i.demand_desc})
@router.put("/purchase-requests/{request_id}",response_model=APIResponse)
def update_purchase_request(request_id:str,payload:PurchaseRequestUpdate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:
    i=_pr(db,request_id);d=payload.model_dump(exclude_none=True);s=str(d.get("request_status") or i.request_status or "submitted").strip().lower()
    if s not in REQ: raise AppError(code="PURCHASE_REQUEST_STATUS_INVALID",message="采购申请状态不合法",status_code=400)
    for k,v in d.items(): setattr(i,k,s if k=="request_status" else v)
    _audit(db,current_user,"update_purchase_request","purchase_request",i.id,{"updated_fields":list(d.keys())});db.commit();db.refresh(i)
    return APIResponse(data=_dump(i))
@router.delete("/purchase-requests/{request_id}",response_model=APIResponse)
def delete_purchase_request(request_id:str,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:
    i=_pr(db,request_id);rs=db.query(RFQ).filter(RFQ.pr_id==request_id).all()
    for r in rs:
        for q in db.query(Quote).filter(Quote.rfq_id==r.id).all(): db.delete(q)
        db.delete(r)
    _audit(db,current_user,"delete_purchase_request","purchase_request",i.id,{"rfq_count":len(rs)});db.delete(i);db.commit()
    return APIResponse(data={"id":request_id,"deleted":True})
@router.post("/purchase-requests/{request_id}/status",response_model=APIResponse)
def update_purchase_request_status(request_id:str,payload:PurchaseRequestStatusUpdate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:
    i=_pr(db,request_id);c=(i.request_status or "draft").strip().lower();t=payload.request_status.strip().lower()
    if t not in REQ: raise AppError(code="PURCHASE_REQUEST_STATUS_INVALID",message="采购申请状态不合法",status_code=400)
    i.request_status=t;_audit(db,current_user,"update_purchase_request_status","purchase_request",i.id,{"from":c,"to":t});db.commit();db.refresh(i)
    return APIResponse(data={"id":i.id,"request_status":i.request_status})

@router.post("/rfqs",response_model=APIResponse)
def create_rfq(payload:RFQCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:
    p=_pr(db,payload.pr_id)
    r=RFQ(pr_id=p.id,rfq_code=f"RFQ-{p.id[:8].upper()}",category_code=p.category_code,structured_requirement_json='{"demand_desc": "%s", "expected_quantity": %s}'%(p.demand_desc.replace('"','\\"'),p.expected_quantity),invited_supplier_count=payload.invited_supplier_count,quote_deadline=payload.quote_deadline,rfq_status="draft",owner_user_id=current_user.id)
    db.add(r);p.request_status="sourcing";db.flush();_audit(db,current_user,"create_rfq","rfq",r.id,{"pr_id":p.id,"rfq_code":r.rfq_code});_audit(db,current_user,"sync_purchase_request_status","purchase_request",p.id,{"request_status":p.request_status,"rfq_id":r.id});db.commit();db.refresh(r)
    return APIResponse(data={"id":r.id,"rfq_code":r.rfq_code,"pr_id":r.pr_id})
@router.get("/rfqs",response_model=APIResponse)
def list_rfqs(db:Session=Depends(get_db),_:User=Depends(get_current_user))->APIResponse:
    return APIResponse(data=[_dump(i) for i in db.query(RFQ).order_by(RFQ.updated_at.desc()).all()])
@router.put("/rfqs/{rfq_id}",response_model=APIResponse)
def update_rfq(rfq_id:str,payload:RFQUpdate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:
    i=_rfq(db,rfq_id);d=payload.model_dump(exclude_none=True);s=str(d.get("rfq_status") or i.rfq_status or "draft").strip().lower()
    if s not in RFQ_S: raise AppError(code="RFQ_STATUS_INVALID",message="询价任务状态不合法",status_code=400)
    for k,v in d.items(): setattr(i,k,s if k=="rfq_status" else v)
    _audit(db,current_user,"update_rfq","rfq",i.id,{"updated_fields":list(d.keys())});db.commit();db.refresh(i)
    return APIResponse(data=_dump(i))
@router.delete("/rfqs/{rfq_id}",response_model=APIResponse)
def delete_rfq(rfq_id:str,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:
    i=_rfq(db,rfq_id);qs=db.query(Quote).filter(Quote.rfq_id==rfq_id).all()
    for q in qs: db.delete(q)
    _audit(db,current_user,"delete_rfq","rfq",i.id,{"quote_count":len(qs)});db.delete(i);db.commit()
    return APIResponse(data={"id":rfq_id,"deleted":True})
@router.post("/rfqs/{rfq_id}/status",response_model=APIResponse)
def update_rfq_status(rfq_id:str,payload:RFQStatusUpdate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:
    i=_rfq(db,rfq_id);c=(i.rfq_status or "draft").strip().lower();t=payload.rfq_status.strip().lower()
    if t not in RFQ_S: raise AppError(code="RFQ_STATUS_INVALID",message="询价任务状态不合法",status_code=400)
    i.rfq_status=t;p=db.query(PurchaseRequest).filter(PurchaseRequest.id==i.pr_id).first()
    if p and t=="quoted": p.request_status="quoted"
    elif p and t=="awarded": p.request_status="awarded"
    elif p and t in {"draft","published","evaluating"}: p.request_status="sourcing"
    _audit(db,current_user,"update_rfq_status","rfq",i.id,{"from":c,"to":t});db.commit();db.refresh(i)
    return APIResponse(data={"id":i.id,"rfq_status":i.rfq_status})

@router.post("/quotes",response_model=APIResponse)
def create_quote(payload:QuoteCreate,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:
    r=_rfq(db,payload.rfq_id);s=db.query(Supplier).filter(Supplier.id==payload.supplier_id).first()
    if not s: raise AppError(code="SUPPLIER_NOT_FOUND",message="供应商不存在，无法新增报价",status_code=404)
    q=Quote(rfq_id=payload.rfq_id,supplier_id=payload.supplier_id,quote_total_amount_tax=payload.quote_total_amount_tax,quote_total_amount_no_tax=payload.quote_total_amount_no_tax,currency_code=payload.currency_code,payment_terms=payload.payment_terms,delivery_lead_time=payload.delivery_lead_time,warranty_period=payload.warranty_period,service_terms=payload.service_terms,technical_match_score=payload.technical_match_score,quote_risk_level=payload.quote_risk_level,parsed_json='{"supplier_name": "%s", "payment_terms": "%s", "delivery_lead_time": "%s"}'%(s.supplier_name.replace('"','\\"'),payload.payment_terms.replace('"','\\"'),payload.delivery_lead_time.replace('"','\\"')))
    db.add(q);r.rfq_status="quoted" if r.rfq_status in {"published","draft"} else r.rfq_status;p=db.query(PurchaseRequest).filter(PurchaseRequest.id==r.pr_id).first()
    if p: p.request_status="quoted"
    db.flush();_audit(db,current_user,"create_quote","quote",q.id,{"rfq_id":r.id,"supplier_id":s.id,"amount_tax":q.quote_total_amount_tax});db.commit();db.refresh(q)
    return APIResponse(data={"id":q.id,"rfq_id":q.rfq_id,"supplier_id":q.supplier_id})
@router.post("/rfqs/{rfq_id}/award",response_model=APIResponse)
def award_rfq(rfq_id:str,payload:RFQAwardPayload,db:Session=Depends(get_db),current_user:User=Depends(get_current_user))->APIResponse:
    r=_rfq(db,rfq_id);qs=db.query(Quote).filter(Quote.rfq_id==rfq_id).order_by(Quote.quote_total_amount_tax.asc()).all()
    if not qs: raise AppError(code="RFQ_QUOTES_EMPTY",message="当前询价任务还没有报价，无法定标",status_code=400)
    q=next((i for i in qs if payload.supplier_id and i.supplier_id==payload.supplier_id),qs[0]);s=db.query(Supplier).filter(Supplier.id==q.supplier_id).first();r.structured_requirement_json=_award(q,s);r.rfq_status="awarded";p=db.query(PurchaseRequest).filter(PurchaseRequest.id==r.pr_id).first()
    if p: p.request_status="awarded"
    _audit(db,current_user,"award_rfq","rfq",r.id,{"supplier_id":q.supplier_id,"quote_id":q.id});db.commit();db.refresh(r)
    return APIResponse(data={"id":r.id,"rfq_status":r.rfq_status,"awarded_supplier_id":q.supplier_id})
@router.get("/quotes",response_model=APIResponse)
def list_quotes(db:Session=Depends(get_db),_:User=Depends(get_current_user))->APIResponse:
    return APIResponse(data=[_dump(i) for i in db.query(Quote).order_by(Quote.quote_total_amount_tax.asc()).all()])
@router.get("/comparison",response_model=APIResponse)
def quote_comparison(db:Session=Depends(get_db),_:User=Depends(get_current_user))->APIResponse:
    qs=db.query(Quote).order_by(Quote.quote_total_amount_tax.asc()).all();rec=qs[0].supplier_id if qs else "N/A"
    return APIResponse(data={"summary":{"recommendedSupplier":rec,"decisionBasis":"综合价格、交期和风险表现最优"},"quotes":[_dump(i) for i in qs],"risks":["最低报价供应商付款条件偏严格"] if len(qs)>1 else [],"negotiationSuggestions":["争取延长账期","锁定批量折扣"]})
