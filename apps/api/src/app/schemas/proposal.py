from pydantic import BaseModel


class ProposalSummary(BaseModel):
    id: str
    project_name: str
    industry_code: str
    bid_type: str
    proposal_status: str
    risk_level: str
    approval_status: str
    owner_user_id: str

