from pydantic import BaseModel, EmailStr, Field


class LeadCreate(BaseModel):
    source_channel: str = "manual"
    source_detail: str = ""
    company_name: str
    contact_name: str
    contact_title: str = ""
    phone: str = ""
    email: EmailStr | None = None
    industry_code: str = ""
    industry_name: str = ""
    company_size: str = ""
    region_code: str = ""
    website_url: str = ""
    demand_summary: str = ""
    budget_signal: str = ""
    project_stage: str = ""
    owner_user_id: str = ""


class LeadUpdate(BaseModel):
    company_name: str | None = None
    contact_name: str | None = None
    contact_title: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    industry_name: str | None = None
    company_size: str | None = None
    region_code: str | None = None
    demand_summary: str | None = None
    project_stage: str | None = None
    owner_user_id: str | None = None
    lead_status: str | None = None
    invalid_reason: str | None = None


class LeadStatusUpdate(BaseModel):
    lead_status: str = Field(..., min_length=1)
    invalid_reason: str = ""


class FollowupCreate(BaseModel):
    lead_id: str
    followup_type: str = "call"
    followup_channel: str = "phone"
    followup_content: str = Field(min_length=1)
    followup_result: str = ""
    next_action: str = ""
