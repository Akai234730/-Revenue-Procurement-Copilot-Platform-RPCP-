import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { AlertBanner } from '../components/AlertBanner';
import { PageHeader } from '../components/PageHeader';
import { QueryState } from '../components/QueryState';
import { StatusBadge } from '../components/StatusBadge';
import { fetcher, poster, APIError } from '../lib/api';
import type { IntegrationStatus, MetricsOverview, UnifiedTaskResult } from '../types';

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

function getTaskTypeLabel(value: string): string {
  const labels: Record<string, string> = {
    sync_leads_to_crm: '同步线索到客户系统',
  };
  return labels[value] ?? value.replaceAll('_', ' ');
}

export function SettingsPage() {
  const usersQuery = useQuery({
    queryKey: ['users'],
    queryFn: () => fetcher<Array<Record<string, unknown>>>('/auth/users'),
  });
  const integrations = useQuery({
    queryKey: ['integrations'],
    queryFn: () => fetcher<IntegrationStatus[]>('/integrations/systems'),
  });
  const tasks = useQuery({
    queryKey: ['integration-tasks'],
    queryFn: () => fetcher<UnifiedTaskResult[]>('/integrations/tasks'),
  });
  const metrics = useQuery({
    queryKey: ['settings-runtime-metrics'],
    queryFn: () => fetcher<MetricsOverview>('/health/metrics'),
  });
  const [taskResult, setTaskResult] = useState<UnifiedTaskResult | null>(null);
  const [taskError, setTaskError] = useState('');

  const createSyncTask = async () => {
    setTaskError('');
    try {
      const result = await poster<UnifiedTaskResult>('/integrations/tasks', {
        task_type: 'sync_leads_to_crm',
        source_system: 'platform',
        target_system: 'crm',
        payload: { scope: 'lead' },
      });
      setTaskResult(result);
      await tasks.refetch();
    } catch (error) {
      if (error instanceof APIError) {
        setTaskError(`${error.code}: ${error.message}`);
      } else {
        setTaskError('统一任务创建失败，请稍后重试。');
      }
    }
  };

  const errorCount = metrics.data?.error_count ?? 0;

  return (
    <div className="page-stack">
      <PageHeader
        title="系统设置"
        description="管理组织、角色权限、系统集成、数据源、安全策略与审计配置，并统一查看系统运行与集成状态。"
      />
      {errorCount > 0 ? (
        <AlertBanner
          title="系统运行异常提示"
          message={`当前平台累计 ${errorCount} 次异常，请优先检查集成任务与接口错误码。`}
          tone="danger"
        />
      ) : null}
      {taskError ? <AlertBanner title="任务创建异常" message={taskError} tone="danger" /> : null}
      <div className="panel-grid two-columns">
        <div className="panel insight-panel">
          <div className="section-header">
            <h3>权限与组织</h3>
            <span className="muted-inline">身份与权限</span>
          </div>
          <div className="signal-list">
            <div className="signal-item">
              <strong>统一身份权限体系</strong>
              <span>支持基于角色与属性的权限控制、单点登录、数据域隔离与知识权限过滤，满足复杂组织协同场景。</span>
            </div>
            <div className="signal-item">
              <strong>组织与角色治理</strong>
              <span>面向管理员统一配置用户、角色和部门边界，建立标准化权限模型。</span>
            </div>
          </div>
        </div>
        <div className="panel">
          <div className="section-header">
            <h3>系统集成</h3>
            <button className="primary-btn" onClick={createSyncTask}>创建同步任务</button>
          </div>
          <QueryState
            isLoading={integrations.isLoading}
            error={integrations.error}
            empty={!integrations.isLoading && !integrations.error && (integrations.data?.length ?? 0) === 0}
            emptyTitle="暂无集成系统"
            emptyMessage="请先接入客户管理、企业资源计划、供应商管理、办公协同等系统。"
          />
          <div className="list-table">
            {(integrations.data ?? []).map((item, index) => (
              <div className="list-row dense" key={index}>
                <strong>{item.system_name}</strong>
                <span>{getSystemLabel(item.system_code)}</span>
                <span><StatusBadge value={item.status} /></span>
                <span>{item.last_sync_at}</span>
                <span>{String(item.detail.scope ?? '')}</span>
              </div>
            ))}
          </div>
          {taskResult ? (
            <div className="detail-block">
              <strong>最新统一任务</strong>
              <p>{taskResult.message}</p>
              <ul>
                {taskResult.next_actions.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      </div>
      <div className="panel-grid two-columns">
        <div className="panel">
          <div className="section-header">
            <h3>集成任务追踪</h3>
            <span className="muted-inline">任务状态</span>
          </div>
          <QueryState
            isLoading={tasks.isLoading}
            error={tasks.error}
            empty={!tasks.isLoading && !tasks.error && (tasks.data?.length ?? 0) === 0}
            emptyTitle="暂无集成任务"
            emptyMessage="创建同步任务后，可在此查看统一任务状态。"
          />
          <div className="list-table">
            {(tasks.data ?? []).map((item, index) => (
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
        <div className="panel">
          <div className="section-header">
            <h3>用户与角色</h3>
            <button className="primary-btn">新建用户</button>
          </div>
          <QueryState
            isLoading={usersQuery.isLoading}
            error={usersQuery.error}
            empty={!usersQuery.isLoading && !usersQuery.error && (usersQuery.data?.length ?? 0) === 0}
            emptyTitle="暂无用户数据"
            emptyMessage="请先创建用户和角色。"
          />
          <div className="list-table">
            {(usersQuery.data ?? []).map((item, index) => (
              <div className="list-row dense" key={index}>
                <strong>{String(item.display_name)}</strong>
                <span>{String(item.username)}</span>
                <span>{String(item.dept_id)}</span>
                <span><StatusBadge value={String(item.status)} /></span>
                <span>{Array.isArray(item.roles) ? item.roles.join(', ') : ''}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
