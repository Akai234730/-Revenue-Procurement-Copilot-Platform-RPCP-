from pydantic import BaseModel, Field


class ProposalCreate(BaseModel):
    customer_id: str = ""
    project_name: str
    industry_code: str = ""
    bid_type: str = "rfp"
    owner_user_id: str = ""


class ProposalUpdate(BaseModel):
    customer_id: str | None = None
    project_name: str | None = None
    industry_code: str | None = None
    bid_type: str | None = None
    risk_level: str | None = None
    approval_status: str | None = None
    owner_user_id: str | None = None


class ProposalRfpUpdate(BaseModel):
    rfp_doc_uri: str = ""
    rfp_content: str = ""


class ProposalStatusUpdate(BaseModel):
    proposal_status: str = Field(..., min_length=1)


class SupplierCreate(BaseModel):
    supplier_name: str
    supplier_code: str = ""
    supplier_category: str = ""
    qualification_level: str = ""
    region_code: str = ""


class SupplierUpdate(BaseModel):
    supplier_name: str | None = None
    supplier_code: str | None = None
    supplier_category: str | None = None
    qualification_level: str | None = None
    region_code: str | None = None
    major_products: str | None = None
    contact_person: str | None = None
    contact_phone: str | None = None
    settlement_terms: str | None = None
    supplier_status: str | None = None
    strategic_supplier_flag: str | None = None


class SupplierStatusUpdate(BaseModel):
    supplier_status: str = Field(..., min_length=1)


class PurchaseRequestCreate(BaseModel):
    applicant_user_id: str = ""
    dept_id: str = ""
    category_code: str = ""
    demand_desc: str
    expected_quantity: int = 0
    budget_amount: float = 0


class PurchaseRequestUpdate(BaseModel):
    applicant_user_id: str | None = None
    dept_id: str | None = None
    category_code: str | None = None
    demand_desc: str | None = None
    expected_quantity: int | None = None
    budget_amount: float | None = None
    request_status: str | None = None


class PurchaseRequestStatusUpdate(BaseModel):
    request_status: str = Field(..., min_length=1)


class RFQCreate(BaseModel):
    pr_id: str
    invited_supplier_count: int = 3
    quote_deadline: str = ""


class RFQUpdate(BaseModel):
    invited_supplier_count: int | None = None
    quote_deadline: str | None = None
    rfq_doc_uri: str | None = None
    rfq_status: str | None = None


class RFQStatusUpdate(BaseModel):
    rfq_status: str = Field(..., min_length=1)


class QuoteCreate(BaseModel):
    rfq_id: str
    supplier_id: str
    quote_total_amount_tax: float = 0
    quote_total_amount_no_tax: float = 0
    currency_code: str = "CNY"
    payment_terms: str = ""
    delivery_lead_time: str = ""
    warranty_period: str = ""
    service_terms: str = ""
    technical_match_score: float = 0
    quote_risk_level: str = "medium"


class RFQAwardPayload(BaseModel):
    supplier_id: str | None = None
