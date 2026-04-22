from io import BytesIO
import re

from docx import Document
from fastapi import APIRouter, Depends, File, Form, UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.identity import User
from app.models.proposal import ProposalProject
from app.schemas.common import APIResponse
from app.schemas.domain_write import ProposalCreate, ProposalStatusUpdate, ProposalUpdate
from app.services.audit_service import AuditService

router = APIRouter()
_ALLOWED_PROPOSAL_STATUSES = {"draft", "rfp_parsed", "generated", "reviewing", "approved", "rejected"}
_SUPPORTED_TEXT_EXTENSIONS = {"txt", "md", "json", "csv", "html", "htm", "xml", "pdf", "doc", "docx"}


def _dump(item):
    return {k: v for k, v in item.__dict__.items() if k != "_sa_instance_state"}


def _normalize_lines(rfp_content: str) -> list[str]:
    return [line.strip() for line in rfp_content.splitlines() if line.strip()]


def _pick_background(lines: list[str]) -> str:
    for line in lines:
        if len(line) >= 18:
            return line[:120]
    return "招标文件已上传，待进一步补充业务背景信息。"


def _pick_scope(lines: list[str]) -> list[str]:
    candidates = [line for line in lines if 6 <= len(line) <= 40][:4]
    if candidates:
        return candidates
    return ["技术方案设计与交付", "商务响应与报价组织", "实施计划与验收安排"]


def _pick_keywords(item: ProposalProject, rfp_content: str) -> list[str]:
    keywords = []
    for candidate in [item.project_name, item.industry_code, "技术方案", "商务响应", "实施计划", "风险控制", "交付验收"]:
        if candidate and candidate not in keywords:
            keywords.append(str(candidate))
    if "招标" in rfp_content and "招标公告" not in keywords:
        keywords.append("招标公告")
    return keywords[:6]


def _build_requirement_json(item: ProposalProject, rfp_content: str) -> str:
    lines = _normalize_lines(rfp_content)
    project_background = _pick_background(lines)
    scope_items = _pick_scope(lines)
    keyword_items = _pick_keywords(item, rfp_content)
    requirement_points = [
        "1. 项目背景\n%s" % project_background,
        "2. 建设范围\n%s" % "\n".join(f"- {scope}" for scope in scope_items[:3]),
        "3. 投标关注重点\n- 技术响应完整性\n- 商务条款匹配度\n- 实施计划可执行性\n- 交付与验收风险控制",
        "4. 建议输出物\n- 技术方案主文\n- 商务响应清单\n- 项目实施计划\n- 风险澄清与偏差说明",
        "5. 关键词\n%s" % "、".join(keyword_items),
    ]
    return "\n\n".join(requirement_points)


def _build_scoring_rule_json(rfp_content: str) -> str:
    lines = _normalize_lines(rfp_content)
    notes = _pick_background(lines)
    scoring_sections = [
        "1. 评分结构",
        "- 技术部分：45 分，重点关注方案完整性、架构先进性、实施可行性与验收保障。",
        "- 商务部分：35 分，重点关注报价合理性、条款响应度、交付保障与服务承诺。",
        "- 交付部分：20 分，重点关注项目周期、资源投入、风险预案与运维支持。",
        "",
        "2. 评审建议",
        "- 技术方案需逐章映射招标需求，避免只给概述。",
        "- 商务响应应明确偏差项、付款条件、保修与服务边界。",
        "- 实施计划建议按里程碑、角色分工、验收标准进行展开。",
        "",
        "3. 评审备注",
        f"- 文档摘录：{notes[:140]}",
    ]
    return "\n".join(scoring_sections)


def _extract_pdf_text(raw: bytes) -> str:
    reader = PdfReader(BytesIO(raw))
    return "\n".join((page.extract_text() or "").strip() for page in reader.pages).strip()


def _extract_docx_text(raw: bytes) -> str:
    document = Document(BytesIO(raw))
    return "\n".join(paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()).strip()


def _read_uploaded_rfp(file: UploadFile | None) -> tuple[str, str]:
    if not file or not file.filename:
        return "", ""
    extension = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    if extension not in _SUPPORTED_TEXT_EXTENSIONS:
        raise AppError(code="RFP_FILE_TYPE_UNSUPPORTED", message="当前仅支持 txt、md、json、csv、html、xml、pdf、doc、docx 等文件格式", status_code=400)
    raw = file.file.read()
    if extension in {"txt", "md", "json", "csv", "html", "htm", "xml"}:
        return file.filename, raw.decode("utf-8", errors="ignore")
    if extension == "pdf":
        return file.filename, _extract_pdf_text(raw)
    if extension == "docx":
        return file.filename, _extract_docx_text(raw)
    return file.filename, f"[已上传文件：{file.filename}]\n当前版本暂不支持直接提取 .doc 正文，请另存为 .docx 或补充粘贴核心内容。"


@router.get("", response_model=APIResponse)
def list_proposals(db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> APIResponse:
    items = db.query(ProposalProject).order_by(ProposalProject.updated_at.desc()).all()
    return APIResponse(data=[_dump(item) for item in items])


@router.post("", response_model=APIResponse)
def create_proposal(payload: ProposalCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> APIResponse:
    item = ProposalProject(customer_id=payload.customer_id, project_name=payload.project_name, industry_code=payload.industry_code, bid_type=payload.bid_type, owner_user_id=payload.owner_user_id or current_user.id, proposal_status="draft", risk_level="medium", approval_status="pending")
    db.add(item)
    db.flush()
    AuditService(db).persist_event(AuditService(db).build_event(module_name="proposal", action_name="create_proposal", operator_id=current_user.id, target_type="proposal", target_id=item.id, result="success", detail={"project_name": item.project_name}))
    db.commit()
    db.refresh(item)
    return APIResponse(data={"id": item.id, "project_name": item.project_name})


@router.get("/{proposal_id}", response_model=APIResponse)
def get_proposal(proposal_id: str, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> APIResponse:
    item = db.query(ProposalProject).filter(ProposalProject.id == proposal_id).first()
    if not item:
        raise AppError(code="PROPOSAL_NOT_FOUND", message="方案项目不存在", status_code=404)
    return APIResponse(data=_dump(item))


@router.put("/{proposal_id}", response_model=APIResponse)
def update_proposal(proposal_id: str, payload: ProposalUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> APIResponse:
    item = db.query(ProposalProject).filter(ProposalProject.id == proposal_id).first()
    if not item:
        raise AppError(code="PROPOSAL_NOT_FOUND", message="方案项目不存在", status_code=404)
    updated_fields = payload.model_dump(exclude_none=True)
    for field, value in updated_fields.items():
        setattr(item, field, value)
    item.version_no = int(item.version_no or 1) + 1
    AuditService(db).persist_event(AuditService(db).build_event(module_name="proposal", action_name="update_proposal", operator_id=current_user.id, target_type="proposal", target_id=item.id, result="success", detail={"updated_fields": list(updated_fields.keys()), "version_no": item.version_no}))
    db.commit()
    db.refresh(item)
    return APIResponse(data=_dump(item))


@router.delete("/{proposal_id}", response_model=APIResponse)
def delete_proposal(proposal_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> APIResponse:
    item = db.query(ProposalProject).filter(ProposalProject.id == proposal_id).first()
    if not item:
        raise AppError(code="PROPOSAL_NOT_FOUND", message="方案项目不存在", status_code=404)
    AuditService(db).persist_event(AuditService(db).build_event(module_name="proposal", action_name="delete_proposal", operator_id=current_user.id, target_type="proposal", target_id=item.id, result="success", detail={"project_name": item.project_name}))
    db.delete(item)
    db.commit()
    return APIResponse(data={"id": proposal_id, "deleted": True})


@router.post("/{proposal_id}/rfp", response_model=APIResponse)
def update_proposal_rfp(proposal_id: str, rfp_content: str = Form(default=""), file: UploadFile | None = File(default=None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> APIResponse:
    item = db.query(ProposalProject).filter(ProposalProject.id == proposal_id).first()
    if not item:
        raise AppError(code="PROPOSAL_NOT_FOUND", message="方案项目不存在", status_code=404)
    uploaded_name, uploaded_content = _read_uploaded_rfp(file)
    merged_content = "\n\n".join(filter(None, [uploaded_content, rfp_content])).strip()
    if not merged_content:
        raise AppError(code="RFP_CONTENT_REQUIRED", message="请上传招标文件或补充粘贴内容", status_code=400)
    item.rfp_doc_uri = uploaded_name or item.rfp_doc_uri
    item.requirement_json = _build_requirement_json(item, merged_content)
    item.scoring_rule_json = _build_scoring_rule_json(merged_content)
    item.version_no = int(item.version_no or 1) + 1
    item.proposal_status = "rfp_parsed"
    item.approval_status = "pending"
    AuditService(db).persist_event(AuditService(db).build_event(module_name="proposal", action_name="update_proposal_rfp", operator_id=current_user.id, target_type="proposal", target_id=item.id, result="success", detail={"version_no": item.version_no, "rfp_doc_uri": item.rfp_doc_uri}))
    db.commit()
    db.refresh(item)
    return APIResponse(data=_dump(item))


@router.post("/{proposal_id}/status", response_model=APIResponse)
def update_proposal_status(proposal_id: str, payload: ProposalStatusUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> APIResponse:
    item = db.query(ProposalProject).filter(ProposalProject.id == proposal_id).first()
    if not item:
        raise AppError(code="PROPOSAL_NOT_FOUND", message="方案项目不存在", status_code=404)
    current_status = (item.proposal_status or "draft").strip().lower()
    target_status = payload.proposal_status.strip().lower()
    if target_status not in _ALLOWED_PROPOSAL_STATUSES:
        raise AppError(code="PROPOSAL_STATUS_INVALID", message="方案状态不合法", status_code=400)
    item.proposal_status = target_status
    if target_status == "approved":
        item.approval_status = "approved"
    elif target_status == "reviewing":
        item.approval_status = "in_review"
    else:
        item.approval_status = "pending"
    item.version_no = int(item.version_no or 1) + 1
    AuditService(db).persist_event(AuditService(db).build_event(module_name="proposal", action_name="update_proposal_status", operator_id=current_user.id, target_type="proposal", target_id=item.id, result="success", detail={"from": current_status, "to": target_status, "version_no": item.version_no}))
    db.commit()
    db.refresh(item)
    return APIResponse(data=_dump(item))
