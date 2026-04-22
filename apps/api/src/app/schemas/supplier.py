from pydantic import BaseModel


class SupplierSummary(BaseModel):
    id: str
    supplier_name: str
    supplier_category: str
    qualification_level: str
    supplier_status: str
    region_code: str


class SupplierEvaluationSummary(BaseModel):
    id: str
    supplier_id: str
    evaluation_period: str
    total_score: float
    risk_level: str
    cooperation_suggestion: str
