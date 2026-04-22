from sqlalchemy import Boolean, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class Lead(BaseEntity):
    __tablename__ = "leads"

    source_channel: Mapped[str] = mapped_column(String(64), default="manual")
    source_detail: Mapped[str] = mapped_column(String(128), default="")
    company_name: Mapped[str] = mapped_column(String(255))
    contact_name: Mapped[str] = mapped_column(String(128))
    contact_title: Mapped[str] = mapped_column(String(128), default="")
    phone: Mapped[str] = mapped_column(String(64), default="")
    email: Mapped[str] = mapped_column(String(255), default="")
    industry_code: Mapped[str] = mapped_column(String(64), default="")
    industry_name: Mapped[str] = mapped_column(String(128), default="")
    company_size: Mapped[str] = mapped_column(String(64), default="")
    region_code: Mapped[str] = mapped_column(String(64), default="")
    website_url: Mapped[str] = mapped_column(String(255), default="")
    demand_summary: Mapped[str] = mapped_column(Text, default="")
    budget_signal: Mapped[str] = mapped_column(String(128), default="")
    project_stage: Mapped[str] = mapped_column(String(64), default="")
    owner_user_id: Mapped[str] = mapped_column(String(64), default="")
    ai_profile_summary: Mapped[str] = mapped_column(Text, default="")
    ai_lead_score: Mapped[float] = mapped_column(Float, default=0)
    ai_maturity_level: Mapped[str] = mapped_column(String(32), default="low")
    ai_priority_level: Mapped[str] = mapped_column(String(16), default="P3")
    ai_next_action: Mapped[str] = mapped_column(Text, default="")
    ai_confidence: Mapped[float] = mapped_column(Float, default=0)
    ai_risk_flag: Mapped[str] = mapped_column(Text, default="[]")
    lead_status: Mapped[str] = mapped_column(String(32), default="new")
    crm_sync_status: Mapped[str] = mapped_column(String(32), default="pending")
    invalid_reason: Mapped[str] = mapped_column(String(255), default="")
    archived: Mapped[bool] = mapped_column(Boolean, default=False)


class FollowupRecord(BaseEntity):
    __tablename__ = "followup_records"

    lead_id: Mapped[str] = mapped_column(String(64), index=True)
    followup_type: Mapped[str] = mapped_column(String(64), default="call")
    followup_channel: Mapped[str] = mapped_column(String(64), default="phone")
    followup_content: Mapped[str] = mapped_column(Text, default="")
    followup_result: Mapped[str] = mapped_column(String(128), default="")
    next_action: Mapped[str] = mapped_column(Text, default="")
    recorder_user_id: Mapped[str] = mapped_column(String(64), default="system")
    ai_generated_flag: Mapped[bool] = mapped_column(Boolean, default=False)
