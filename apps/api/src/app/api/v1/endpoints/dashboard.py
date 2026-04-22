from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.lead import Lead
from app.models.procurement import Quote
from app.models.proposal import ProposalProject
from app.models.supplier import SupplierEvaluation
from app.schemas.common import APIResponse

router = APIRouter()


def _dump(item):
    return {k: v for k, v in item.__dict__.items() if k != "_sa_instance_state"}


@router.get("/overview", response_model=APIResponse)
def overview(db: Session = Depends(get_db)) -> APIResponse:
    leads = db.query(Lead).order_by(Lead.ai_lead_score.desc()).limit(5).all()
    proposals = db.query(ProposalProject).order_by(ProposalProject.updated_at.desc()).limit(5).all()
    evaluations = db.query(SupplierEvaluation).order_by(SupplierEvaluation.total_score.desc()).limit(5).all()
    quotes = db.query(Quote).order_by(Quote.quote_total_amount_tax.asc()).limit(5).all()

    return APIResponse(
        data={
            "metrics": {
                "todoCount": db.query(Lead).filter(Lead.lead_status.in_(["new", "contacted"])).count(),
                "urgentCount": db.query(Lead).filter(Lead.ai_priority_level == "P1").count(),
                "approvalCount": db.query(ProposalProject).filter(ProposalProject.approval_status != "approved").count(),
                "riskCount": db.query(SupplierEvaluation).filter(SupplierEvaluation.risk_level.in_(["high", "critical"])).count(),
                "leadTrend": [12, 18, 20, 23, 25, 28, len(leads) + 30],
                "proposalTrend": [3, 5, 6, 6, 8, 10, len(proposals) + 10],
                "supplierRiskDistribution": [
                    db.query(SupplierEvaluation).filter(SupplierEvaluation.risk_level == "low").count(),
                    db.query(SupplierEvaluation).filter(SupplierEvaluation.risk_level == "medium").count(),
                    db.query(SupplierEvaluation).filter(SupplierEvaluation.risk_level == "high").count(),
                ],
                "procurementSavingsTrend": [1.8, 2.4, 2.9, 3.2, 3.8],
            },
            "topLeads": [_dump(item) for item in leads],
            "pendingProposals": [_dump(item) for item in proposals],
            "supplierEvaluations": [_dump(item) for item in evaluations],
            "activeQuotes": [_dump(item) for item in quotes],
        }
    )
