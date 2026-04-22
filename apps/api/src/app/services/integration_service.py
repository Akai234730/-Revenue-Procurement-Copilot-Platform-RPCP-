from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class IntegrationEndpoint:
    system_code: str
    system_name: str
    enabled: bool
    status: str
    last_sync_at: str
    owner: str
    detail: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class UnifiedTask:
    task_id: str
    task_type: str
    source_system: str
    target_system: str
    status: str
    message: str
    next_actions: list[str] = field(default_factory=list)
    created_at: str = ""


class IntegrationService:
    _task_store: list[UnifiedTask] = []

    def list_integrations(self) -> list[IntegrationEndpoint]:
        return [
            IntegrationEndpoint(
                system_code="crm",
                system_name="CRM",
                enabled=True,
                status="connected",
                last_sync_at="2026-04-20T09:30:00",
                owner="sales-platform",
                detail={"scope": "客户、线索、跟进"},
            ),
            IntegrationEndpoint(
                system_code="erp",
                system_name="ERP",
                enabled=True,
                status="connected",
                last_sync_at="2026-04-20T09:25:00",
                owner="finance-platform",
                detail={"scope": "订单、合同、预算"},
            ),
            IntegrationEndpoint(
                system_code="srm",
                system_name="SRM",
                enabled=True,
                status="warning",
                last_sync_at="2026-04-20T08:58:00",
                owner="procurement-platform",
                detail={"scope": "供应商、询价、评估"},
            ),
            IntegrationEndpoint(
                system_code="oa",
                system_name="OA",
                enabled=True,
                status="connected",
                last_sync_at="2026-04-20T09:10:00",
                owner="office-platform",
                detail={"scope": "审批、通知、待办"},
            ),
            IntegrationEndpoint(
                system_code="dms",
                system_name="文档系统",
                enabled=True,
                status="connected",
                last_sync_at="2026-04-20T09:12:00",
                owner="knowledge-platform",
                detail={"scope": "合同、方案、制度文档"},
            ),
            IntegrationEndpoint(
                system_code="msg",
                system_name="消息平台",
                enabled=True,
                status="connected",
                last_sync_at="2026-04-20T09:18:00",
                owner="notification-platform",
                detail={"scope": "站内信、IM、机器人通知"},
            ),
        ]

    def dispatch_task(self, task_type: str, source_system: str, target_system: str, payload: dict[str, Any]) -> UnifiedTask:
        timestamp = datetime.now(UTC).strftime('%Y%m%d%H%M%S')
        task = UnifiedTask(
            task_id=f"integration_{task_type}_{timestamp}",
            task_type=task_type,
            source_system=source_system,
            target_system=target_system,
            status="queued",
            message=f"已创建跨系统任务：{task_type}",
            next_actions=[
                f"校验 {source_system} 数据完整性",
                f"投递到 {target_system} 接口网关",
                "回写执行结果与审计日志",
            ],
            created_at=datetime.now(UTC).isoformat(),
        )
        self._task_store.insert(0, task)
        self._task_store = self._task_store[:20]
        return task

    def list_tasks(self) -> list[UnifiedTask]:
        return self._task_store
