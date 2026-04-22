from pydantic import BaseModel


class LeadSummary(BaseModel):
    id: str
    company_name: str
    contact_name: str
    industry_name: str
    source_channel: str
    ai_lead_score: float
    ai_maturity_level: str
    ai_priority_level: str
    ai_next_action: str
    crm_sync_status: str
    lead_status: str


class FollowupSummary(BaseModel):
    id: str
    lead_id: str
    followup_type: str
    followup_channel: str
    followup_content: str
    followup_result: str
    next_action: str
