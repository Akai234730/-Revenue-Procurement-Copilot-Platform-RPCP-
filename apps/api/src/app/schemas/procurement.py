from pydantic import BaseModel


class PurchaseRequestSummary(BaseModel):
    id: str
    dept_id: str
    category_code: str
    demand_desc: str
    expected_quantity: int
    budget_amount: float
    request_status: str


class RFQSummary(BaseModel):
    id: str
    pr_id: str
    rfq_code: str
    category_code: str
    invited_supplier_count: int
    quote_deadline: str
    rfq_status: str


class QuoteSummary(BaseModel):
    id: str
    rfq_id: str
    supplier_id: str
    quote_total_amount_tax: float
    quote_total_amount_no_tax: float
    currency_code: str
    quote_risk_level: str
