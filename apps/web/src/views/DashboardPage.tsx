import { useQuery } from '@tanstack/react-query';

import { AlertBanner } from '../components/AlertBanner';
import { PageHeader } from '../components/PageHeader';
import { QueryState } from '../components/QueryState';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { fetcher } from '../lib/api';
import type { DashboardOverview, MetricsOverview, RuntimeStatus } from '../types';

export function DashboardPage() {
  const dashboardQuery = useQuery({
    queryKey: ['dashboard-overview'],
    queryFn: () => fetcher<DashboardOverview>('/dashboard/overview'),
  });
  const runtime = useQuery({
    queryKey: ['runtime-status'],
    queryFn: () => fetcher<RuntimeStatus>('/health'),
  });
  const metricsOverview = useQuery({
    queryKey: ['runtime-metrics'],
    queryFn: () => fetcher<MetricsOverview>('/health/metrics'),
  });

  const metrics = dashboardQuery.data?.metrics;
  const degradedCount = metricsOverview.data?.degraded_count ?? 0;

  return (
    <div className="page-stack">
      <PageHeader
        title="首页工作台"
        description="以统一上下文串联销售、采购、供应商与经营动作，让智能分析决策、人工复核与业务执行处于同一工作流。"
      />

      <section className="hero-panel">
        <div className="hero-panel__main">
          <div className="hero-panel__eyebrow">经营驾驶舱</div>
          <h3>今天的重点经营动作与平台状态一目了然</h3>
          <p>
            面向经营负责人、销售负责人和采购负责人，统一展示待办、风险、协同审批与智能分析运行信号，帮助你在一个界面内完成判断与推进。
          </p>
          <div className="hero-panel__meta">
            <span>服务名称：{runtime.data?.service ?? 'rpcp-api'}</span>
            <span>运行环境：{runtime.data?.environment ?? '-'}</span>
            <span>模型服务：{runtime.data?.provider ?? '-'}</span>
          </div>
        </div>
        <div className="hero-panel__side">
          <div className="hero-kpi">
            <strong>{metricsOverview.data?.request_count ?? 0}</strong>
            <span>累计调度请求</span>
          </div>
          <div className="hero-kpi warning">
            <strong>{degradedCount}</strong>
            <span>需要关注的降级执行</span>
          </div>
        </div>
      </section>

      {degradedCount > 0 ? (
        <AlertBanner
          title="平台降级提示"
          message={`当前已有 ${degradedCount} 次降级执行，请优先排查智能分析模型配置与超时链路。`}
          tone="warning"
        />
      ) : null}

      <section className="stats-grid">
        <StatCard title="我的待办" value={metrics?.todoCount ?? '-'} hint="今日待推进事项" />
        <StatCard title="紧急事项" value={metrics?.urgentCount ?? '-'} hint="建议优先处理" tone="warning" />
        <StatCard title="待审批" value={metrics?.approvalCount ?? '-'} hint="跨部门协同动作" />
        <StatCard title="风险预警" value={metrics?.riskCount ?? '-'} hint="需要人工复核" tone="danger" />
      </section>

      <section className="panel-grid two-columns">
        <div className="panel insight-panel">
          <div className="section-header">
            <h3>平台运行摘要</h3>
            <span className="muted-inline">运行状态</span>
          </div>
          <QueryState
            isLoading={runtime.isLoading || metricsOverview.isLoading}
            error={runtime.error ?? metricsOverview.error}
            empty={!runtime.isLoading && !metricsOverview.isLoading && !runtime.data && !metricsOverview.data}
            emptyTitle="暂无运行状态"
            emptyMessage="服务状态接口暂时不可用。"
          />
          {runtime.data && metricsOverview.data ? (
            <div className="detail-grid">
              <div>
                <strong>服务 / 环境</strong>
                <span>{runtime.data.service} · {runtime.data.environment}</span>
              </div>
              <div>
                <strong>模型配置</strong>
                <span>{runtime.data.provider} / {runtime.data.model_name}</span>
              </div>
              <div>
                <strong>请求总量</strong>
                <span>{metricsOverview.data.request_count}</span>
              </div>
              <div>
                <strong>智能分析历史 / 审计</strong>
                <span>{metricsOverview.data.ai_task_count} / {metricsOverview.data.audit_log_count}</span>
              </div>
            </div>
          ) : null}
        </div>

        <div className="panel insight-panel">
          <div className="section-header">
            <h3>经营提示</h3>
            <span className="muted-inline">智能关注重点</span>
          </div>
          <div className="signal-list">
            <div className="signal-item">
              <strong>优先推进高价值线索跟进</strong>
              <span>将高意向线索转化为下一步行动，优先处理具有明确预算与时间窗口的客户。</span>
            </div>
            <div className="signal-item">
              <strong>同步关注采购报价风险</strong>
              <span>对高风险报价和交付不确定性项目保持复核，避免后续执行偏差。</span>
            </div>
            <div className="signal-item">
              <strong>结合供应商评分安排复审</strong>
              <span>对近期得分波动或风险等级上升的供应商安排评估与替代预案。</span>
            </div>
          </div>
        </div>
      </section>

      <QueryState
        isLoading={dashboardQuery.isLoading}
        error={dashboardQuery.error}
        empty={!dashboardQuery.isLoading && !dashboardQuery.error && !dashboardQuery.data}
        emptyTitle="暂无经营数据"
        emptyMessage="请先完成业务数据初始化。"
      />

      {dashboardQuery.data ? (
        <>
          <section className="panel-grid two-columns">
            <div className="panel">
              <div className="section-header">
                <h3>高优先级线索</h3>
                <span className="muted-inline">重点线索</span>
              </div>
              <div className="list-table">
                {(dashboardQuery.data.topLeads ?? []).map((item, index) => (
                  <div className="list-row" key={index}>
                    <strong>{String(item.company_name)}</strong>
                    <span><StatusBadge value={String(item.ai_priority_level)} /></span>
                    <span>{String(item.ai_next_action)}</span>
                  </div>
                ))}
              </div>
            </div>
            <div className="panel">
              <div className="section-header">
                <h3>待处理方案项目</h3>
                <span className="muted-inline">方案队列</span>
              </div>
              <div className="list-table">
                {(dashboardQuery.data.pendingProposals ?? []).map((item, index) => (
                  <div className="list-row" key={index}>
                    <strong>{String(item.project_name)}</strong>
                    <span><StatusBadge value={String(item.proposal_status)} /></span>
                    <span><StatusBadge value={String(item.risk_level)} /></span>
                  </div>
                ))}
              </div>
            </div>
          </section>

          <section className="panel-grid two-columns">
            <div className="panel">
              <div className="section-header">
                <h3>待评估供应商</h3>
                <span className="muted-inline">供应商评审</span>
              </div>
              <div className="list-table">
                {(dashboardQuery.data.supplierEvaluations ?? []).map((item, index) => (
                  <div className="list-row" key={index}>
                    <strong>{String(item.evaluation_period)}</strong>
                    <span>评分 {String(item.total_score)}</span>
                    <span><StatusBadge value={String(item.cooperation_suggestion)} /></span>
                  </div>
                ))}
              </div>
            </div>
            <div className="panel">
              <div className="section-header">
                <h3>活跃报价任务</h3>
                <span className="muted-inline">采购报价</span>
              </div>
              <div className="list-table">
                {(dashboardQuery.data.activeQuotes ?? []).map((item, index) => (
                  <div className="list-row" key={index}>
                    <strong>{String(item.currency_code)} {String(item.quote_total_amount_tax)}</strong>
                    <span><StatusBadge value={String(item.quote_risk_level)} /></span>
                    <span>供应商 {String(item.supplier_id)}</span>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </>
      ) : null}
    </div>
  );
}
