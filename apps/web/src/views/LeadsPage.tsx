import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { AIActionPanel } from '../components/AIActionPanel';
import { LeadCreateForm } from '../components/LeadCreateForm';
import { LeadDetailCard } from '../components/LeadDetailCard';
import { PageHeader } from '../components/PageHeader';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { fetcher } from '../lib/api';
import type { LeadRecord } from '../types';

export function LeadsPage() {
  const { data, refetch } = useQuery({ queryKey: ['leads'], queryFn: () => fetcher<LeadRecord[]>('/leads') });
  const [selectedLeadId, setSelectedLeadId] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const selectedLead = useMemo(() => data?.find((item) => item.id === selectedLeadId) ?? data?.[0] ?? null, [data, selectedLeadId]);
  const leadCount = data?.length ?? 0;
  const highPriorityCount = (data ?? []).filter((item) => item.ai_priority_level === 'high' || item.ai_priority_level === 'P1').length;
  const avgScore = leadCount ? Math.round((data ?? []).reduce((sum, item) => sum + (item.ai_lead_score ?? 0), 0) / leadCount) : 0;
  const handleSelectLead = (leadId: string) => { setSelectedLeadId(leadId); setExpanded(true); };
  const resetWorkspace = () => { setExpanded(false); };
  return (
    <div className="page-stack">
      <PageHeader title="销售线索筛选与跟进" description="围绕高价值客户识别、评分解释、线索推进和销售跟进动作，构建更高密度、更可执行的销售智能工作台。" />
      <section className="hero-panel"><div className="hero-panel__main"><div className="hero-panel__eyebrow">线索智能分析</div><h3>把客户画像、优先级、下一步动作与跟进执行放在同一个界面里</h3><p>支持销售负责人和一线销售基于智能评分快速识别高价值线索，并将推荐动作、客户信息和跟进记录统一沉淀到一套工作流中。</p><div className="hero-panel__meta"><span>优先跟进高价值客户</span><span>统一记录跟进动作</span><span>支持 AI 辅助话术生成</span></div></div><div className="hero-panel__side"><div className="hero-kpi success"><strong>{leadCount}</strong><span>当前线索总数</span></div><div className="hero-kpi warning"><strong>{highPriorityCount}</strong><span>高优先级线索</span></div></div></section>
      <section className="stats-grid"><StatCard title="线索总量" value={leadCount} hint="当前可跟进客户数" /><StatCard title="高优先级" value={highPriorityCount} hint="建议优先推进" tone="warning" /><StatCard title="平均评分" value={avgScore} hint="智能评分均值" tone="success" /><StatCard title="当前选中" value={selectedLead?.company_name ?? '-'} hint="正在查看的客户" /></section>
      <div className="panel filter-bar"><span>来源渠道</span><span>行业</span><span>地区</span><span>评分区间</span><span>成熟度</span><span>负责人</span></div>
      {showForm ? <div className="panel"><div className="section-header"><h3>新建线索</h3><button className="ghost-btn" onClick={() => setShowForm(false)}>收起表单</button></div><LeadCreateForm onCreated={() => void refetch()} /></div> : null}
      <div className={`workspace-grid workspace-grid--lead ${expanded ? 'is-expanded' : ''}`}><div className="panel workspace-panel workspace-panel--list"><div className="section-header workspace-header"><div><h3>线索列表</h3><span className="muted-inline">选择左侧线索后，左右工作区会同步展开，并可一键恢复默认尺寸</span></div><div className="workspace-actions"><button className="primary-btn" onClick={() => setShowForm((prev) => !prev)}>{showForm ? '关闭新建' : '新建线索'}</button><button className="ghost-btn" type="button" onClick={resetWorkspace} disabled={!expanded}>恢复默认尺寸</button></div></div><div className="list-table scroll-area workspace-scroll workspace-scroll--list">{(data ?? []).map((item) => <button className={`list-button ${selectedLead?.id === item.id ? 'is-selected' : ''}`} key={item.id} onClick={() => handleSelectLead(item.id)}><div className={`list-row dense ${selectedLead?.id === item.id ? 'is-selected' : ''}`}><strong>{item.company_name}</strong><span>{item.industry_name}</span><span>评分 {item.ai_lead_score}</span><span><StatusBadge value={item.ai_priority_level} /></span><span>{item.ai_next_action}</span></div></button>)}</div></div><LeadDetailCard lead={selectedLead} onChanged={() => void refetch()} expanded={expanded} onResetLayout={resetWorkspace} /></div>
      <AIActionPanel title="智能销售跟进助手" scene="lead_followup" entityId={selectedLead?.id} context={{ company_name: selectedLead?.company_name, contact_name: selectedLead?.contact_name, contact_title: selectedLead?.contact_title, industry_name: selectedLead?.industry_name, source_channel: selectedLead?.source_channel, company_size: selectedLead?.company_size, region_code: selectedLead?.region_code, demand_summary: selectedLead?.demand_summary, project_stage: selectedLead?.project_stage, lead_status: selectedLead?.lead_status, ai_lead_score: selectedLead?.ai_lead_score, ai_maturity_level: selectedLead?.ai_maturity_level, priority: selectedLead?.ai_priority_level, ai_next_action: selectedLead?.ai_next_action, crm_sync_status: selectedLead?.crm_sync_status }} onExecuted={() => void refetch()} />
      <div className="panel-grid two-columns"><div className="panel insight-panel"><div className="section-header"><h3>评分解释</h3><span className="muted-inline">评分逻辑说明</span></div><div className="signal-list"><div className="signal-item"><strong>客户画像与高价值信号</strong><span>基于行业、规模、需求摘要与项目阶段识别高价值客户和潜在成交机会。</span></div><div className="signal-item"><strong>风险信号识别</strong><span>结合成熟度、跟进节奏和项目阶段，识别可能延迟、失联或推进阻塞的风险。</span></div><div className="signal-item"><strong>下一步推荐动作</strong><span>输出更具体的跟进建议、推荐话术与客户管理系统回写动作，帮助团队形成标准化推进路径。</span></div></div></div><div className="panel insight-panel"><div className="section-header"><h3>销售经理视图</h3><span className="muted-inline">管理者洞察</span></div><div className="signal-list"><div className="signal-item"><strong>团队线索热力分布</strong><span>快速查看高质量线索集中行业、地区与来源渠道，辅助资源分配。</span></div><div className="signal-item"><strong>超时未跟进排行</strong><span>关注长时间未推进的重要线索，避免销售漏跟和商机损失。</span></div><div className="signal-item"><strong>AI 建议采纳情况</strong><span>沉淀智能推荐动作的使用情况，为销售流程和提示策略持续优化提供依据。</span></div></div></div></div>
    </div>
  );
}
