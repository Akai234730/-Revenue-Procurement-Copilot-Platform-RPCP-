from fastapi import APIRouter

from app.api.v1.endpoints import ai, audit, auth, dashboard, health, integrations, knowledge, leads, proposals, procurement, suppliers

api_router = APIRouter()
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(proposals.router, prefix="/proposals", tags=["proposals"])
api_router.include_router(suppliers.router, prefix="/suppliers", tags=["suppliers"])
api_router.include_router(procurement.router, prefix="/procurement", tags=["procurement"])
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(integrations.router, prefix="/integrations", tags=["integrations"])
