from pydantic import BaseModel


class KnowledgeDocumentSummary(BaseModel):
    id: str
    doc_name: str
    domain_type: str
    source_system: str
    permission_scope: str
    vector_status: str


class AuditLogSummary(BaseModel):
    id: str
    module_name: str
    action_name: str
    operator_id: str
    result: str
