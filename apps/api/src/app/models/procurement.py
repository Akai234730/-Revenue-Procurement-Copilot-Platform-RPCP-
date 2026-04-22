from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class PurchaseRequest(BaseEntity):
    __tablename__ = "purchase_requests"

    applicant_user_id: Mapped[str] = mapped_column(String(64), default="")
    dept_id: Mapped[str] = mapped_column(String(64), default="")
    category_code: Mapped[str] = mapped_column(String(64), default="")
    demand_desc: Mapped[str] = mapped_column(Text, default="")
    spec_doc_uri: Mapped[str] = mapped_column(String(500), default="")
    expected_quantity: Mapped[int] = mapped_column(Integer, default=0)
    expected_delivery_date: Mapped[str] = mapped_column(String(64), default="")
    budget_amount: Mapped[float] = mapped_column(Float, default=0)
    request_status: Mapped[str] = mapped_column(String(32), default="draft")


class RFQ(BaseEntity):
    __tablename__ = "rfqs"

    pr_id: Mapped[str] = mapped_column(String(64), index=True)
    rfq_code: Mapped[str] = mapped_column(String(64), default="")
    category_code: Mapped[str] = mapped_column(String(64), default="")
    structured_requirement_json: Mapped[str] = mapped_column(Text, default="{}")
    invited_supplier_count: Mapped[int] = mapped_column(Integer, default=0)
    rfq_doc_uri: Mapped[str] = mapped_column(String(500), default="")
    quote_deadline: Mapped[str] = mapped_column(String(64), default="")
    rfq_status: Mapped[str] = mapped_column(String(32), default="draft")
    owner_user_id: Mapped[str] = mapped_column(String(64), default="")


class Quote(BaseEntity):
    __tablename__ = "quotes"

    rfq_id: Mapped[str] = mapped_column(String(64), index=True)
    supplier_id: Mapped[str] = mapped_column(String(64), index=True)
    quote_doc_uri: Mapped[str] = mapped_column(String(500), default="")
    quote_total_amount_tax: Mapped[float] = mapped_column(Float, default=0)
    quote_total_amount_no_tax: Mapped[float] = mapped_column(Float, default=0)
    currency_code: Mapped[str] = mapped_column(String(16), default="CNY")
    payment_terms: Mapped[str] = mapped_column(Text, default="")
    delivery_lead_time: Mapped[str] = mapped_column(String(64), default="")
    warranty_period: Mapped[str] = mapped_column(String(64), default="")
    service_terms: Mapped[str] = mapped_column(Text, default="")
    technical_match_score: Mapped[float] = mapped_column(Float, default=0)
    quote_risk_level: Mapped[str] = mapped_column(String(32), default="medium")
    parsed_json: Mapped[str] = mapped_column(Text, default="{}")
