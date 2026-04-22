import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.platform import KnowledgeDocument


class KnowledgeService:
    SCENE_KEYWORDS: dict[str, list[str]] = {
        "proposal_generation": ["proposal", "rfp", "招标", "售前", "方案"],
        "procurement_analysis": ["procurement", "采购", "rfq", "quote", "供应商"],
        "supplier_assessment": ["supplier", "供应商", "履约", "评估", "整改"],
    }

    def __init__(self, db: Session):
        self.db = db

    def retrieve_sources(self, scene: str, limit: int = 3) -> list[dict[str, Any]]:
        keywords = self.SCENE_KEYWORDS.get(scene, [])
        documents = self.db.query(KnowledgeDocument).order_by(KnowledgeDocument.updated_at.desc()).all()
        ranked: list[tuple[int, KnowledgeDocument]] = []
        for item in documents:
            haystack = " ".join([
                item.doc_name or "",
                item.domain_type or "",
                item.source_system or "",
                item.tags or "",
            ]).lower()
            score = sum(1 for keyword in keywords if keyword.lower() in haystack)
            if score > 0 or not keywords:
                ranked.append((score, item))
        ranked.sort(key=lambda row: (row[0], str(row[1].updated_at or "")), reverse=True)
        selected = [item for _, item in ranked[:limit]]
        return [
            {
                "doc_name": item.doc_name,
                "domain_type": item.domain_type,
                "source_system": item.source_system,
                "version_no": item.version_no,
                "quality_score": item.quality_score,
                "tags": json.loads(item.tags) if item.tags else [],
            }
            for item in selected
        ]
