import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { AlertBanner } from '../components/AlertBanner';
import { AIActionPanel } from '../components/AIActionPanel';
import { AIHistoryPanel } from '../components/AIHistoryPanel';
import { AuditLogPanel } from '../components/AuditLogPanel';
import { IntegrationTaskPanel } from '../components/IntegrationTaskPanel';
import { PageHeader } from '../components/PageHeader';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { fetcher } from '../lib/api';
import type { AIExecutionResult, MetricsOverview, ProposalRecord, RFQRecord, RuntimeStatus } from '../types';

export function OperationsPage() {
  const [opsAiResult, setOpsAiResult] = useState<AIExecutionResult | null>(null);

  const runtime = useQuery({ queryKey: ['ops-runtime-status'], queryFn: () => fetcher<RuntimeStatus>('/health') });
  const metrics = useQuery({ queryKey: ['ops-runtime-metrics'], queryFn: () => fetcher<MetricsOverview>('/health/metrics') });
  const proposals = useQuery({ queryKey: ['ops-proposals'], queryFn: () => fetcher<ProposalRecord[]>('/proposals') });
  const rfqs = useQuery({ queryKey: ['ops-rfqs'], queryFn: () => fetcher<RFQRecord[]>('/procurement/rfqs') });

  const degradedCount = metrics.data?.degraded_count ?? 0;
  const errorCount = metrics.data?.error_count ?? 0;
  const generatedProposalCount = (proposals.data ?? []).filter((item) => String(item.proposal_status).toLowerCase() === 'generated').length;
  const reviewingProposalCount = (proposals.data ?? []).filter((item) => String(item.proposal_status).toLowerCase() === 'reviewing').length;
  const awardedRfqCount = (rfqs.data ?? []).filter((item) => String(item.rfq_status).toLowerCase() === 'awarded').length;
  const quotedRfqCount = (rfqs.data ?? []).filter((item) => String(item.rfq_status).toLowerCase() === 'quoted').length;

  return (
    <div className="page-stack">
      <PageHeader title="运营中心" description="围绕智能分析编排质量、调用趋势、降级情况、统一任务和审计信息，形成稳定可运营的智能平台中台视图。" />

      <section className="hero-panel ops-hero">
        <div className="hero-panel__main">
          <div className="hero-panel__eyebrow">运营智能分析</div>
          <h3>从运行指标、异常、审计到任务闭环，统一管理平台质量</h3>
          <p>让平台负责人在一个页面里同时看到模型服务、降级趋势、错误情况、智能分析历史和跨系统任务，建立可追踪的运营面板。</p>
          <div className="hero-panel__meta"><span>模型服务：{runtime.data?.provider ?? '-'}</span><span>模型名称：{runtime.data?.model_name ?? '-'}</span><span>运行环境：{runtime.data?.environment ?? '-'}</span><span>运行状态：{runtime.data?.status ?? '-'}</span></div>
        </div>
        <div className="hero-panel__side">
          <div className="hero-kpi success"><strong>{runtime.data?.provider ?? '-'}</strong><span>当前模型服务</span></div>
          <div className="hero-kpi danger"><strong>{errorCount}</strong><span>当前统计周期异常数</span></div>
        </div>
      </section>

      {degradedCount > 0 ? <AlertBanner title="运行降级提示" message={`当前检测到 ${degradedCount} 次智能分析降级执行，请关注主模型配置、超时策略与备用路径。`} tone="warning" /> : null}
      {errorCount > 0 ? <AlertBanner title="运行异常提示" message={`当前统计到 ${errorCount} 次错误，请结合审计日志与统一任务结果进行排查。`} tone="danger" /> : null}

      <div className="stats-grid">
        <StatCard title="当前模型服务" value={runtime.data?.provider ?? '-'} hint="当前执行模型来源" tone="success" />
        <StatCard title="运行环境" value={runtime.data?.environment ?? '-'} hint="当前环境配置" />
        <StatCard title="降级次数" value={degradedCount} hint="触发兜底执行次数" tone="warning" />
        <StatCard title="错误次数" value={errorCount} hint="当前统计周期" tone="danger" />
      </div>

      <section className="panel-grid two-columns">
        <div className="panel insight-panel">
          <div className="section-header"><h3>运行观测</h3><span className="muted-inline">运行状态与平台指标</span></div>
          <div className="detail-grid"><div><strong>服务状态</strong><span><StatusBadge value={runtime.data?.status ?? '-'} /></span></div><div><strong>数据库</strong><span>{runtime.data?.database ?? '-'}</span></div><div><strong>智能任务总量</strong><span>{metrics.data?.ai_task_count ?? 0}</span></div><div><strong>统一任务数</strong><span>{metrics.data?.integration_task_count ?? 0}</span></div><div><strong>审计日志量</strong><span>{metrics.data?.audit_log_count ?? 0}</span></div><div><strong>请求总量</strong><span>{metrics.data?.request_count ?? 0}</span></div></div>
        </div>
        <div className="panel insight-panel">
          <div className="section-header"><h3>业务状态分布</h3><span className="muted-inline">核心流程进度快照</span></div>
          <div className="detail-grid"><div><strong>方案已生成</strong><span><StatusBadge value={generatedProposalCount} tone="success" /></span></div><div><strong>方案评审中</strong><span><StatusBadge value={reviewingProposalCount} tone="warning" /></span></div><div><strong>询价单已收齐报价</strong><span><StatusBadge value={quotedRfqCount} tone="warning" /></span></div><div><strong>询价单已定标</strong><span><StatusBadge value={awardedRfqCount} tone="success" /></span></div></div>
        </div>
      </section>

      <section className="panel-grid two-columns">
        <div className="panel insight-panel">
          <div className="section-header"><h3>平台判断</h3><span className="muted-inline">当前平台运营结论</span></div>
          <div className="detail-block"><strong>当前状态结论</strong><p>{errorCount > 0 ? '当前平台存在需优先处理的错误信号，建议结合审计日志、智能分析历史与统一任务结果按场景排查。' : degradedCount > 0 ? '当前平台整体可用，但存在降级执行，建议优先检查主模型服务商的可用性与超时链路。' : '当前平台运行稳定，可继续观察任务执行质量与业务结果一致性。'}</p></div>
        </div>
        <div className="panel insight-panel">
          <div className="section-header"><h3>重点状态样本</h3><span className="muted-inline">近期关键样本</span></div>
          <div className="list-table scroll-area scroll-area--md">{(proposals.data ?? []).slice(0, 3).map((item) => <div className="list-row" key={item.id}><strong>{item.project_name}</strong><span><StatusBadge value={item.proposal_status} /></span><span><StatusBadge value={item.approval_status} /></span></div>)}{(rfqs.data ?? []).slice(0, 3).map((item) => <div className="list-row" key={item.id}><strong>{item.rfq_code}</strong><span><StatusBadge value={item.rfq_status} /></span><span>{item.category_code}</span></div>)}</div>
        </div>
      </section>

      {opsAiResult ? (
        <section className="panel-grid two-columns">
          <div className="panel insight-panel">
            <div className="section-header"><h3>本次运营结论</h3><span className="muted-inline">智能分析已生成平台级判断</span></div>
            <div className="detail-block">
              <strong>结论摘要</strong>
              <p>{opsAiResult.summary}</p>
              <div className="action-row">
                <StatusBadge value={opsAiResult.status} />
                <StatusBadge value={opsAiResult.provider} tone="info" />
              </div>
            </div>
            <div className="detail-block detail-block--scroll">
              <strong>关键洞察</strong>
              <div className="scroll-area scroll-area--sm">
                <ul>
                  {opsAiResult.insights.map((item, index) => (
                    <li key={index}>{item.title}：{item.content}（置信度 {(item.confidence * 100).toFixed(0)}%）</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
          <div className="panel insight-panel">
            <div className="section-header"><h3>今日重点动作</h3><span className="muted-inline">建议优先推进的运营动作</span></div>
            <div className="detail-block detail-block--scroll">
              <strong>风险与依据</strong>
              <div className="scroll-area scroll-area--sm">
                <ul>
                  {opsAiResult.evidence.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="detail-block detail-block--scroll">
              <strong>下一步动作</strong>
              <div className="scroll-area scroll-area--sm">
                <ul>
                  {opsAiResult.next_actions.map((item, index) => (
                    <li key={index}>{item}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </section>
      ) : null}

      <section className="page-stack">
        <div className="section-header">
          <div>
            <h3>智能运营工作区</h3>
            <span className="muted-inline">查看分析结果、历史执行与重点结论</span>
          </div>
        </div>
        <AIActionPanel
          title="智能运营分析助手"
          scene="ops_analysis"
          context={{
            scope: 'global',
            provider: runtime.data?.provider,
            environment: runtime.data?.environment,
            service_status: runtime.data?.status,
            request_count: metrics.data?.request_count,
            error_count: errorCount,
            degraded_count: degradedCount,
            ai_task_count: metrics.data?.ai_task_count,
            integration_task_count: metrics.data?.integration_task_count,
            audit_log_count: metrics.data?.audit_log_count,
            generated_proposal_count: generatedProposalCount,
            reviewing_proposal_count: reviewingProposalCount,
            quoted_rfq_count: quotedRfqCount,
            awarded_rfq_count: awardedRfqCount,
          }}
          onExecuted={setOpsAiResult}
        />
        <AIHistoryPanel />
      </section>

      <section className="page-stack">
        <div className="section-header">
          <div>
            <h3>平台追踪工作区</h3>
            <span className="muted-inline">统一查看审计日志与跨系统任务流转</span>
          </div>
        </div>
        <div className="panel-grid two-columns"><AuditLogPanel /><IntegrationTaskPanel /></div>
      </section>
    </div>
  );
}
