import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { AIActionPanel } from '../components/AIActionPanel';
import { EmptyState } from '../components/EmptyState';
import { PageHeader } from '../components/PageHeader';
import { QueryState } from '../components/QueryState';
import { AlertBanner } from '../components/AlertBanner';
import { StatusBadge } from '../components/StatusBadge';
import { fetcher } from '../lib/api';
import type { MetricsOverview } from '../types';

function getKnowledgeDomainLabel(value: string): string {
  const labels: Record<string, string> = {
    general: '通用知识',
    sales: '销售知识',
    procurement: '采购知识',
    supplier: '供应商知识',
    proposal: '方案知识',
  };
  return labels[value] ?? value;
}

export function KnowledgePage() {
  const query = useQuery({
    queryKey: ['knowledge-documents'],
    queryFn: () => fetcher<Array<Record<string, unknown>>>('/knowledge/documents'),
  });
  const metrics = useQuery({
    queryKey: ['knowledge-runtime-metrics'],
    queryFn: () => fetcher<MetricsOverview>('/health/metrics'),
  });

  const degradedCount = metrics.data?.degraded_count ?? 0;

  return (
    <div className="page-stack">
      <PageHeader title="知识中心" description="统一管理销售、采购与公共知识资产，支撑知识检索增强与智能体生成。" />
      {degradedCount > 0 ? <AlertBanner title="知识服务降级提示" message={`当前平台检测到 ${degradedCount} 次降级执行，知识治理结果可能受影响。`} tone="warning" /> : null}
      <div className="panel">
        <h3>知识文档</h3>
        <QueryState
          isLoading={query.isLoading}
          error={query.error}
          empty={!query.isLoading && !query.error && (query.data?.length ?? 0) === 0}
          emptyTitle="暂无知识文档"
          emptyMessage="请先同步文档系统或上传知识资产。"
        />
        {(query.data ?? []).length > 0 ? (
          (query.data ?? []).map((item, index) => (
            <div className="list-row dense" key={index}>
              <strong>{String(item.doc_name)}</strong>
              <span>{getKnowledgeDomainLabel(String(item.domain_type))}</span>
              <span><StatusBadge value={String(item.vector_status)} /></span>
            </div>
          ))
        ) : null}
      </div>
      {query.data ? (
        <AIActionPanel
          title="智能知识治理助手"
          scene="ops_analysis"
          context={{ document_count: query.data.length, module: 'knowledge' }}
        />
      ) : (
        <EmptyState title="知识治理待启动" message="待知识文档可用后，可继续运行智能知识治理分析。" />
      )}
    </div>
  );
}
