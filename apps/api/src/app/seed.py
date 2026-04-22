import json

from app.core.crypto import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models import (
    AITaskExecution,
    AuditLog,
    FollowupRecord,
    KnowledgeDocument,
    Lead,
    Permission,
    ProposalProject,
    PurchaseRequest,
    Quote,
    RFQ,
    Role,
    Supplier,
    SupplierEvaluation,
    User,
)


PERMISSIONS = [
    ("查看审计日志", "audit:view", "查看审计日志"),
    ("管理用户", "auth:user_manage", "创建和管理用户"),
    ("执行AI任务", "ai:execute", "运行平台AI能力"),
]


def ensure_admin(db):
    admin_role = db.query(Role).filter(Role.code == "admin").first()
    if not admin_role:
        admin_role = Role(name="管理员", code="admin", description="系统管理员")
        db.add(admin_role)
        db.flush()

    for name, code, description in PERMISSIONS:
        permission = db.query(Permission).filter(Permission.code == code).first()
        if not permission:
            permission = Permission(name=name, code=code, description=description)
            db.add(permission)
            db.flush()
        if permission not in admin_role.permissions:
            admin_role.permissions.append(permission)

    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            username="admin",
            display_name="系统管理员",
            email="admin@example.com",
            password_hash=hash_password("admin123"),
            dept_id="it",
            title="平台管理员",
        )
        db.add(admin)
        db.flush()
    if admin_role not in admin.roles:
        admin.roles.append(admin_role)
    return admin


def ensure_leads(db, admin):
    if db.query(Lead).count() > 0:
        return db.query(Lead).all()
    leads = [
        Lead(company_name="华东智造集团", contact_name="张伟", contact_title="采购总监", phone="13800000001", email="zhangwei@example.com", industry_code="manufacturing", industry_name="制造业", company_size="large", region_code="CN-EAST", demand_summary="希望建设采购协同与供应商管理平台", budget_signal="明确预算", project_stage="需求调研", owner_user_id=admin.id, ai_profile_summary="高潜制造业客户，需求明确", ai_lead_score=92, ai_maturity_level="high", ai_priority_level="P1", ai_next_action="24小时内安排电话沟通并发送制造业案例包", ai_confidence=0.89, ai_risk_flag=json.dumps(["决策链较长"], ensure_ascii=False), lead_status="new", crm_sync_status="synced", source_channel="官网表单"),
        Lead(company_name="星河能源设备有限公司", contact_name="李敏", contact_title="信息化经理", phone="13800000002", email="limin@example.com", industry_code="energy", industry_name="能源", company_size="medium", region_code="CN-NORTH", demand_summary="招采数字化方案咨询", budget_signal="待确认", project_stage="初步沟通", owner_user_id=admin.id, ai_profile_summary="能源行业客户，需进一步厘清预算", ai_lead_score=84, ai_maturity_level="medium", ai_priority_level="P1", ai_next_action="建议邀请售前参加二次需求访谈", ai_confidence=0.76, ai_risk_flag=json.dumps(["预算待确认"], ensure_ascii=False), lead_status="contacted", crm_sync_status="pending", source_channel="展会"),
    ]
    db.add_all(leads)
    db.flush()
    db.add_all([
        FollowupRecord(lead_id=leads[0].id, followup_type="call", followup_channel="phone", followup_content="首次电话沟通，客户关注供应商绩效闭环", followup_result="positive", next_action="发送案例资料并预约演示", recorder_user_id=admin.id, ai_generated_flag=False),
        FollowupRecord(lead_id=leads[1].id, followup_type="meeting", followup_channel="online", followup_content="线上访谈，确认招标节点在下月", followup_result="neutral", next_action="补充行业解决方案", recorder_user_id=admin.id, ai_generated_flag=False),
    ])
    return leads


def ensure_proposals(db, admin):
    if db.query(ProposalProject).count() > 0:
        return db.query(ProposalProject).all()
    items = [
        ProposalProject(customer_id="cust_mfg_001", project_name="制造集团采购数字化项目", industry_code="manufacturing", bid_type="RFP", requirement_json=json.dumps({"modules": ["SRM", "询比价", "审批"]}, ensure_ascii=False), scoring_rule_json=json.dumps({"技术": 60, "商务": 40}, ensure_ascii=False), proposal_status="draft", risk_level="medium", approval_status="pending", owner_user_id=admin.id),
        ProposalProject(customer_id="cust_energy_002", project_name="能源行业供应链协同平台方案", industry_code="energy", bid_type="招投标", requirement_json=json.dumps({"modules": ["供应商评估", "合同协同"]}, ensure_ascii=False), scoring_rule_json=json.dumps({"能力": 50, "案例": 20, "价格": 30}, ensure_ascii=False), proposal_status="review", risk_level="high", approval_status="in_review", owner_user_id=admin.id),
    ]
    db.add_all(items)
    return items


def ensure_suppliers(db, admin):
    if db.query(Supplier).count() > 0:
        return db.query(Supplier).all()
    suppliers = [
        Supplier(supplier_name="金石精密部件有限公司", supplier_code="SUP-001", supplier_category="结构件", qualification_level="A", region_code="CN-EAST", major_products="精密结构件、配套组件", contact_person="王强", contact_phone="13900000001", settlement_terms="月结30天", supplier_status="active", strategic_supplier_flag="true"),
        Supplier(supplier_name="博远电子材料有限公司", supplier_code="SUP-002", supplier_category="电子材料", qualification_level="B", region_code="CN-SOUTH", major_products="电子材料、辅材", contact_person="赵敏", contact_phone="13900000002", settlement_terms="月结45天", supplier_status="risk_watch", strategic_supplier_flag="false"),
    ]
    db.add_all(suppliers)
    db.flush()
    db.add_all([
        SupplierEvaluation(supplier_id=suppliers[0].id, evaluation_period="2026-Q2", price_score=87, delivery_score=91, quality_score=93, service_score=88, risk_score=80, qualification_score=95, strategic_score=90, total_score=88.4, risk_level="medium", cooperation_suggestion="维持合作，重点跟踪交期稳定性", reviewer_user_id=admin.id),
        SupplierEvaluation(supplier_id=suppliers[1].id, evaluation_period="2026-Q2", price_score=82, delivery_score=70, quality_score=76, service_score=72, risk_score=60, qualification_score=78, strategic_score=65, total_score=71.2, risk_level="high", cooperation_suggestion="限制新增订单并启动整改评审", reviewer_user_id=admin.id),
    ])
    return suppliers


def ensure_procurement(db, admin, suppliers):
    if db.query(PurchaseRequest).count() > 0:
        return
    pr = PurchaseRequest(applicant_user_id=admin.id, dept_id="dept_proc_01", category_code="hardware", demand_desc="采购工业控制器及配套附件", expected_quantity=120, expected_delivery_date="2026-05-30", budget_amount=480000, request_status="submitted")
    db.add(pr)
    db.flush()
    rfq = RFQ(pr_id=pr.id, rfq_code="RFQ-2026-001", category_code="hardware", structured_requirement_json=json.dumps({"型号": "PLC", "交期": "30天"}, ensure_ascii=False), invited_supplier_count=2, quote_deadline="2026-05-08", rfq_status="quoting", owner_user_id=admin.id)
    db.add(rfq)
    db.flush()
    db.add_all([
        Quote(rfq_id=rfq.id, supplier_id=suppliers[0].id, quote_total_amount_tax=436000, quote_total_amount_no_tax=385840, currency_code="CNY", payment_terms="30%预付，70%验收后", delivery_lead_time="25天", warranty_period="12个月", technical_match_score=92, quote_risk_level="low", parsed_json=json.dumps({"优势": ["交期稳定", "技术匹配高"]}, ensure_ascii=False)),
        Quote(rfq_id=rfq.id, supplier_id=suppliers[1].id, quote_total_amount_tax=421500, quote_total_amount_no_tax=373009, currency_code="CNY", payment_terms="50%预付", delivery_lead_time="35天", warranty_period="12个月", technical_match_score=81, quote_risk_level="medium", parsed_json=json.dumps({"风险": ["账期偏严格"]}, ensure_ascii=False)),
    ])


def ensure_knowledge(db):
    if db.query(KnowledgeDocument).count() > 0:
        return
    db.add_all([
        KnowledgeDocument(doc_name="制造业售前案例集", domain_type="sales", source_system="knowledge_base", owner_dept="售前中心", permission_scope="internal", vector_status="ready", effective_date="2026-01-01", quality_score="92", tags=json.dumps(["制造业", "售前", "案例"], ensure_ascii=False)),
        KnowledgeDocument(doc_name="供应商评估制度V3", domain_type="procurement", source_system="manual_upload", owner_dept="采购中心", permission_scope="internal", vector_status="ready", effective_date="2026-02-01", quality_score="88", tags=json.dumps(["供应商", "评估", "制度"], ensure_ascii=False)),
    ])


def ensure_platform_records(db, admin, leads, suppliers):
    if db.query(AuditLog).count() == 0:
        db.add_all([
            AuditLog(module_name="lead", action_name="generate_followup_recommendation", operator_id=admin.id, target_type="lead", target_id=leads[0].id, result="success", detail=json.dumps({"summary": "生成销售跟进建议"}, ensure_ascii=False)),
            AuditLog(module_name="procurement", action_name="generate_rfq_document", operator_id=admin.id, target_type="purchase_request", target_id="seed-pr", result="success", detail=json.dumps({"summary": "生成采购询价分析"}, ensure_ascii=False)),
            AuditLog(module_name="supplier", action_name="evaluate_supplier", operator_id=admin.id, target_type="supplier", target_id=suppliers[0].id, result="success", detail=json.dumps({"summary": "生成供应商评估"}, ensure_ascii=False)),
        ])
    if db.query(AITaskExecution).count() == 0:
        db.add_all([
            AITaskExecution(task_id="task_seed_lead_001", scene="lead_followup", agent_name="lead_followup_agent", provider="aliyun_qwen", operator_id=admin.id, entity_id=leads[0].id, status="completed", summary="识别为高优先级制造业客户，建议快速推进演示。", recommendations=json.dumps(["安排售前演示", "发送案例包"], ensure_ascii=False), evidence=json.dumps(["预算明确", "需求边界清晰"], ensure_ascii=False), insights=json.dumps([{"title": "客户成熟度", "content": "已进入需求确认阶段", "confidence": 0.88}], ensure_ascii=False), next_actions=json.dumps(["本周内完成需求澄清", "同步CRM"], ensure_ascii=False), context=json.dumps({"company_name": leads[0].company_name}, ensure_ascii=False), raw_output=json.dumps({"provider": "aliyun_qwen"}, ensure_ascii=False)),
            AITaskExecution(task_id="task_seed_proc_001", scene="procurement_analysis", agent_name="procurement_analysis_agent", provider="aliyun_qwen", operator_id=admin.id, entity_id="", status="degraded", summary="已生成采购建议，建议优先选择低风险报价。", recommendations=json.dumps(["优先选择交期稳定供应商", "争取更优账期"], ensure_ascii=False), evidence=json.dumps(["供应商一技术匹配更高", "供应商二付款条件偏严格"], ensure_ascii=False), insights=json.dumps([{"title": "比价结果", "content": "综合成本与风险后推荐供应商一", "confidence": 0.81}], ensure_ascii=False), next_actions=json.dumps(["发起议价", "提交审批"], ensure_ascii=False), context=json.dumps({"module": "procurement"}, ensure_ascii=False), raw_output=json.dumps({"fallback": "mock"}, ensure_ascii=False)),
        ])


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = ensure_admin(db)
        leads = ensure_leads(db, admin)
        ensure_proposals(db, admin)
        suppliers = ensure_suppliers(db, admin)
        ensure_procurement(db, admin, suppliers)
        ensure_knowledge(db)
        ensure_platform_records(db, admin, leads, suppliers)
        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed()
