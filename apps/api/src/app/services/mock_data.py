from uuid import uuid4


def uid(prefix: str) -> str:
    return f"{prefix}_{str(uuid4())[:8]}"


def dashboard_metrics() -> dict:
    return {
        "todoCount": 18,
        "urgentCount": 6,
        "approvalCount": 4,
        "riskCount": 9,
        "leadTrend": [32, 35, 28, 40, 45, 52, 60],
        "proposalTrend": [5, 8, 7, 10, 13, 12, 15],
        "supplierRiskDistribution": [12, 23, 8],
        "procurementSavingsTrend": [2.1, 3.4, 2.8, 4.2, 5.1],
    }


def lead_list() -> list[dict]:
    return [
        {
            "id": uid("lead"),
            "company_name": "华东智造集团",
            "contact_name": "张伟",
            "industry_name": "制造业",
            "source_channel": "官网表单",
            "ai_lead_score": 92,
            "ai_maturity_level": "high",
            "ai_priority_level": "P1",
            "ai_next_action": "24小时内安排电话沟通并发送制造业标杆案例包",
            "crm_sync_status": "synced",
            "lead_status": "new",
        },
        {
            "id": uid("lead"),
            "company_name": "星河能源设备有限公司",
            "contact_name": "李敏",
            "industry_name": "能源",
            "source_channel": "展会",
            "ai_lead_score": 84,
            "ai_maturity_level": "medium",
            "ai_priority_level": "P1",
            "ai_next_action": "建议邀请售前参加二次需求访谈",
            "crm_sync_status": "pending",
            "lead_status": "contacted",
        },
    ]


def proposal_list() -> list[dict]:
    return [
        {
            "id": uid("proposal"),
            "project_name": "某大型制造集团采购数字化项目",
            "industry_code": "manufacturing",
            "bid_type": "RFP",
            "proposal_status": "draft",
            "risk_level": "medium",
            "approval_status": "pending",
            "owner_user_id": "u_presales_01",
        },
        {
            "id": uid("proposal"),
            "project_name": "能源行业供应链协同平台方案",
            "industry_code": "energy",
            "bid_type": "招投标",
            "proposal_status": "review",
            "risk_level": "high",
            "approval_status": "in_review",
            "owner_user_id": "u_presales_02",
        },
    ]


def supplier_list() -> list[dict]:
    return [
        {
            "id": uid("supplier"),
            "supplier_name": "金石精密部件有限公司",
            "supplier_category": "结构件",
            "qualification_level": "A",
            "supplier_status": "active",
            "region_code": "CN-EAST",
        },
        {
            "id": uid("supplier"),
            "supplier_name": "博远电子材料有限公司",
            "supplier_category": "电子材料",
            "qualification_level": "B",
            "supplier_status": "risk_watch",
            "region_code": "CN-SOUTH",
        },
    ]


def supplier_evaluation_list() -> list[dict]:
    return [
        {
            "id": uid("eval"),
            "supplier_id": uid("supplier"),
            "evaluation_period": "2026-Q2",
            "total_score": 88.4,
            "risk_level": "medium",
            "cooperation_suggestion": "维持合作，重点跟踪交期稳定性",
        },
        {
            "id": uid("eval"),
            "supplier_id": uid("supplier"),
            "evaluation_period": "2026-Q2",
            "total_score": 71.2,
            "risk_level": "high",
            "cooperation_suggestion": "限制新增订单并启动整改评审",
        },
    ]


def purchase_request_list() -> list[dict]:
    return [
        {
            "id": uid("pr"),
            "dept_id": "dept_proc_01",
            "category_code": "hardware",
            "demand_desc": "采购工业控制器及配套附件",
            "expected_quantity": 120,
            "budget_amount": 480000,
            "request_status": "submitted",
        }
    ]


def rfq_list() -> list[dict]:
    return [
        {
            "id": uid("rfq"),
            "pr_id": uid("pr"),
            "rfq_code": "RFQ-2026-001",
            "category_code": "hardware",
            "invited_supplier_count": 4,
            "quote_deadline": "2026-05-08",
            "rfq_status": "quoting",
        }
    ]


def quote_list() -> list[dict]:
    return [
        {
            "id": uid("quote"),
            "rfq_id": uid("rfq"),
            "supplier_id": uid("supplier"),
            "quote_total_amount_tax": 436000,
            "quote_total_amount_no_tax": 385840,
            "currency_code": "CNY",
            "quote_risk_level": "low",
        },
        {
            "id": uid("quote"),
            "rfq_id": uid("rfq"),
            "supplier_id": uid("supplier"),
            "quote_total_amount_tax": 421500,
            "quote_total_amount_no_tax": 373009,
            "currency_code": "CNY",
            "quote_risk_level": "medium",
        },
    ]


def knowledge_docs() -> list[dict]:
    return [
        {
            "id": uid("doc"),
            "doc_name": "制造业售前案例集",
            "domain_type": "sales",
            "source_system": "knowledge_base",
            "permission_scope": "internal",
            "vector_status": "ready",
        },
        {
            "id": uid("doc"),
            "doc_name": "供应商评估制度V3",
            "domain_type": "procurement",
            "source_system": "manual_upload",
            "permission_scope": "internal",
            "vector_status": "ready",
        },
    ]


def audit_logs() -> list[dict]:
    return [
        {
            "id": uid("audit"),
            "module_name": "lead",
            "action_name": "generate_followup_recommendation",
            "operator_id": "u_sales_01",
            "result": "success",
        },
        {
            "id": uid("audit"),
            "module_name": "procurement",
            "action_name": "generate_rfq_document",
            "operator_id": "u_proc_01",
            "result": "success",
        },
    ]
