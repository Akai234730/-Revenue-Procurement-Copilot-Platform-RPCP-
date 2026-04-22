import { useQuery } from '@tanstack/react-query';

import { fetcher } from '../lib/api';
import { StatusBadge } from './StatusBadge';
import type { UnifiedTaskResult } from '../types';

function getTaskTypeLabel(value: string): string {
  const labels: Record<string, string> = {
    sync_leads_to_crm: '同步线索到客户系统',
  };
  return labels[value] ?? value.replaceAll('_', ' ');
}

function getSystemLabel(value: string): string {
  const labels: Record<string, string> = {
    platform: '平台',
    crm: '客户系统',
    erp: '企业资源计划',
    srm: '供应商管理',
    oa: '办公协同',
  };
  return labels[value] ?? value;
}

export function IntegrationTaskPanel() {
  const { data } = useQuery({
    queryKey: ['integration-tasks-ops'],
    queryFn: () => fetcher<UnifiedTaskResult[]>('/integrations/tasks'),
  });

  return (
    <div className="panel insight-panel">
      <div className="section-header">
        <div>
          <h3>集成任务</h3>
          <span className="muted-inline">统一查看跨系统流转、状态与执行反馈</span>
        </div>
        <StatusBadge value={data?.length ?? 0} tone="info" />
      </div>
      <div className="list-table scroll-area scroll-area--lg">
        {(data ?? []).map((item, index) => (
          <div className="list-row dense" key={index}>
            <strong>{getTaskTypeLabel(item.task_type)}</strong>
            <span>{getSystemLabel(item.source_system)} → {getSystemLabel(item.target_system)}</span>
            <span><StatusBadge value={item.status} /></span>
            <span>{item.created_at}</span>
            <span>{item.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
