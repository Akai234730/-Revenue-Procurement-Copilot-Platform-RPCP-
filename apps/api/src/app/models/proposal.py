from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class ProposalProject(BaseEntity):
    __tablename__ = "proposal_projects"

    customer_id: Mapped[str] = mapped_column(String(64), default="")
    project_name: Mapped[str] = mapped_column(String(255))
    industry_code: Mapped[str] = mapped_column(String(64), default="")
    bid_type: Mapped[str] = mapped_column(String(64), default="rfp")
    rfp_doc_uri: Mapped[str] = mapped_column(String(500), default="")
    requirement_json: Mapped[str] = mapped_column(Text, default="{}")
    scoring_rule_json: Mapped[str] = mapped_column(Text, default="{}")
    generated_outline_uri: Mapped[str] = mapped_column(Text, default="")
    technical_draft_uri: Mapped[str] = mapped_column(Text, default="")
    commercial_draft_uri: Mapped[str] = mapped_column(Text, default="")
    version_no: Mapped[int] = mapped_column(Integer, default=1)
    proposal_status: Mapped[str] = mapped_column(String(32), default="draft")
    risk_level: Mapped[str] = mapped_column(String(32), default="medium")
    approval_status: Mapped[str] = mapped_column(String(32), default="pending")
    owner_user_id: Mapped[str] = mapped_column(String(64), default="")
