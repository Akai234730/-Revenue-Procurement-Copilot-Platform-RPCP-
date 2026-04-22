from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseEntity


class Supplier(BaseEntity):
    __tablename__ = "suppliers"

    supplier_name: Mapped[str] = mapped_column(String(255))
    supplier_code: Mapped[str] = mapped_column(String(64), default="")
    supplier_category: Mapped[str] = mapped_column(String(64), default="")
    qualification_level: Mapped[str] = mapped_column(String(64), default="")
    region_code: Mapped[str] = mapped_column(String(64), default="")
    major_products: Mapped[str] = mapped_column(Text, default="")
    contact_person: Mapped[str] = mapped_column(String(128), default="")
    contact_phone: Mapped[str] = mapped_column(String(64), default="")
    tax_no: Mapped[str] = mapped_column(String(64), default="")
    settlement_terms: Mapped[str] = mapped_column(Text, default="")
    supplier_status: Mapped[str] = mapped_column(String(32), default="active")
    strategic_supplier_flag: Mapped[str] = mapped_column(String(16), default="false")


class SupplierEvaluation(BaseEntity):
    __tablename__ = "supplier_evaluations"

    supplier_id: Mapped[str] = mapped_column(String(64), index=True)
    evaluation_period: Mapped[str] = mapped_column(String(32), default="")
    price_score: Mapped[float] = mapped_column(Float, default=0)
    delivery_score: Mapped[float] = mapped_column(Float, default=0)
    quality_score: Mapped[float] = mapped_column(Float, default=0)
    service_score: Mapped[float] = mapped_column(Float, default=0)
    risk_score: Mapped[float] = mapped_column(Float, default=0)
    qualification_score: Mapped[float] = mapped_column(Float, default=0)
    strategic_score: Mapped[float] = mapped_column(Float, default=0)
    total_score: Mapped[float] = mapped_column(Float, default=0)
    risk_level: Mapped[str] = mapped_column(String(32), default="medium")
    cooperation_suggestion: Mapped[str] = mapped_column(Text, default="")
    reviewer_user_id: Mapped[str] = mapped_column(String(64), default="system")
