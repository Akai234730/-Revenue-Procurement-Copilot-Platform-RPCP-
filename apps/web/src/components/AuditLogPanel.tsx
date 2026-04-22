import { useQuery } from '@tanstack/react-query';

import { fetcher } from '../lib/api';
import { StatusBadge } from './StatusBadge';
import type { AuditLogRecord } from '../types';

function getModuleLabel(value: string): string {
  const labels: Record<string, string> = {
    ai: '智能分析',
    lead: '线索',
    proposal: '方案',
    supplier: '供应商',
    procurement: '采购',
    audit: '审计',
    integrations: '系统集成',
    auth: '认证',
    dashboard: '工作台',
    knowledge: '知识中心',
    system: '系统',
  };
  return labels[value] ?? value;
}

function getActionLabel(value: string): string {
  const labels: Record<string, string> = {
    orchestrate_completed: '分析执行完成',
    ai_writeback: '分析结果写回',
    ai_generate_followup: '生成跟进记录',
    ai_generate_evaluation: '生成评估记录',
    task_created: '创建分析任务',
  };
  return labels[value] ?? value.replaceAll('_', ' ');
}

export function AuditLogPanel() {
  const { data } = useQuery({
    queryKey: ['audit-logs'],
    queryFn: () => fetcher<AuditLogRecord[]>('/audit/logs'),
  });

  return (
    <div className="panel insight-panel">
      <div className="section-header">
        <div>
          <h3>审计日志</h3>
          <span className="muted-inline">追踪关键动作、结果与操作时间</span>
        </div>
        <StatusBadge value={data?.length ?? 0} tone="info" />
      </div>
      <div className="list-table scroll-area scroll-area--lg">
        {(data ?? []).map((item, index) => (
          <div className="list-row dense" key={index}>
            <strong>{getModuleLabel(item.module_name)}</strong>
            <span>{getActionLabel(item.action_name)}</span>
            <span><StatusBadge value={item.result} /></span>
            <span>{item.created_at}</span>
            <span>{item.operator_id}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
