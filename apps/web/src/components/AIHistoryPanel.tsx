import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { fetcher } from '../lib/api';
import type { AIExecutionDetail, AIExecutionHistoryItem } from '../types';
import { StatusBadge } from './StatusBadge';

function getSceneLabel(scene: string): string {
  const labels: Record<string, string> = {
    lead_followup: '线索跟进',
    proposal_generation: '方案生成',
    supplier_assessment: '供应商评估',
    procurement_analysis: '采购分析',
    ops_analysis: '运营分析',
  };
  return labels[scene] ?? scene;
}

function getStatusLabel(status: string): string {
  const mapping: Record<string, string> = {
    queued: '排队中',
    running: '执行中',
    completed: '执行成功',
    degraded: '降级完成',
    failed: '执行失败',
  };
  return mapping[String(status).toLowerCase()] ?? status;
}

function getProviderLabel(provider: string): string {
  const labels: Record<string, string> = {
    aliyun_qwen: '阿里云通义千问',
    mock: '模拟模型',
    openai: 'OpenAI',
    azure_openai: 'Azure OpenAI',
    local: '本地模型',
  };
  return labels[String(provider).trim()] ?? provider;
}

function getExecutionModeLabel(provider: string): string {
  return provider === 'mock' ? '模拟执行' : '真实模型';
}

function getWritebackFieldLabel(key: string): string {
  const labels: Record<string, string> = {
    lead_id: '线索编号',
    proposal_id: '方案编号',
    supplier_id: '供应商编号',
    rfq_id: '询价任务编号',
    purchase_request_id: '采购申请编号',
    ai_lead_score: '线索评分',
    ai_priority_level: '优先级',
    ai_maturity_level: '成熟度',
    lead_status: '线索状态',
    version_no: '版本号',
    proposal_status: '方案状态',
    generated_outline_written: '方案大纲已写回',
    technical_draft_written: '技术方案已写回',
    commercial_draft_written: '商务方案已写回',
    supplier_status: '供应商状态',
    generated_evaluation_id: '评估记录编号',
    total_score: '综合得分',
    risk_level: '风险等级',
    cooperation_suggestion: '合作建议',
    recommended_supplier_id: '推荐供应商',
    recommended_quote_id: '推荐报价',
  };
  return labels[key] ?? key;
}

function formatDisplayValue(value: unknown): string {
  if (value === null || value === undefined || value === '') return '-';
  if (typeof value === 'boolean') return value ? '是' : '否';
  const labels: Record<string, string> = {
    true: '是',
    false: '否',
    high: '高',
    medium: '中',
    low: '低',
    draft: '草稿',
    reviewing: '评审中',
    approved: '已通过',
    generated: '已生成',
    quoted: '已报价',
    awarded: '已定标',
    sourcing: '寻源中',
    active: '启用',
    suspended: '暂停',
    completed: '执行成功',
    failed: '执行失败',
    degraded: '降级完成',
  };
  const text = String(value);
  return labels[text] ?? text;
}

function parseProviderChain(provider: string) {
  const normalized = String(provider ?? '').trim();
  const parts = normalized.split('->').map((item) => item.trim()).filter(Boolean);
  const primary = parts[0] || '-';
  const fallback = parts.length > 1 ? parts[parts.length - 1] : '';
  const usedMock = parts.includes('mock');
  const isFallback = parts.length > 1;
  return { primary, fallback, usedMock, isFallback, display: parts.map((item) => getProviderLabel(item)).join(' → ') || '-' };
}

function getExecutionTone(status: string, provider: string): 'success' | 'warning' | 'danger' | 'info' | 'neutral' {
  const normalized = String(status).toLowerCase();
  if (normalized === 'failed') return 'danger';
  if (normalized === 'degraded') return 'warning';
  if (parseProviderChain(provider).usedMock) return 'warning';
  if (normalized === 'completed') return 'success';
  return 'info';
}

function getWritebackEntries(context: Record<string, unknown>) {
  const writeback = context.writeback;
  if (!writeback || typeof writeback !== 'object' || Array.isArray(writeback)) return [] as Array<[string, unknown]>;
  return Object.entries(writeback).filter(([, value]) => value !== undefined && value !== null && value !== '');
}

function getKnowledgeSources(context: Record<string, unknown>) {
  const sources = context.knowledge_sources;
  return Array.isArray(sources) ? sources as Array<Record<string, unknown>> : [];
}

function getWritebackObjectLabel(entries: Array<[string, unknown]>) {
  const mapping: Array<[string, string]> = [['lead_id', '线索'], ['proposal_id', '方案'], ['supplier_id', '供应商'], ['rfq_id', '询价任务'], ['purchase_request_id', '采购申请']];
  for (const [key, label] of mapping) {
    if (entries.some(([entryKey]) => entryKey === key)) return label;
  }
  return '分析结果';
}

export function AIHistoryPanel() {
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  const [expanded, setExpanded] = useState(false);
  const [sceneFilter, setSceneFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');
  const [providerFilter, setProviderFilter] = useState('all');
  const [entityFilter, setEntityFilter] = useState('');
  const [quickFilter, setQuickFilter] = useState<'all' | 'failed' | 'degraded'>('all');
  const { data } = useQuery({ queryKey: ['ai-history'], queryFn: () => fetcher<AIExecutionHistoryItem[]>('/ai/history') });
  const detailQuery = useQuery({ queryKey: ['ai-history-detail', selectedTaskId], queryFn: () => fetcher<AIExecutionDetail>(`/ai/history/${selectedTaskId}`), enabled: Boolean(selectedTaskId) });

  const filteredData = useMemo(() => {
    return (data ?? []).filter((item) => {
      const matchesScene = sceneFilter === 'all' || item.scene === sceneFilter;
      const matchesStatus = statusFilter === 'all' || item.status === statusFilter;
      const matchesProvider = providerFilter === 'all' || item.provider.includes(providerFilter);
      const matchesEntity = !entityFilter.trim() || String(item.entity_id ?? '').includes(entityFilter.trim());
      const matchesQuick = quickFilter === 'all' || item.status === quickFilter;
      return matchesScene && matchesStatus && matchesProvider && matchesEntity && matchesQuick;
    });
  }, [data, sceneFilter, statusFilter, providerFilter, entityFilter, quickFilter]);

  const handleSelectTask = (taskId: string) => { setSelectedTaskId(taskId); setExpanded(true); };
  const resetLayout = () => { setExpanded(false); };
  const selectedProviderMeta = detailQuery.data ? parseProviderChain(detailQuery.data.provider) : null;
  const writebackEntries = detailQuery.data ? getWritebackEntries(detailQuery.data.context) : [];
  const knowledgeSources = detailQuery.data ? getKnowledgeSources(detailQuery.data.context) : [];
  const writebackObjectLabel = getWritebackObjectLabel(writebackEntries);
  const sceneOptions = Array.from(new Set((data ?? []).map((item) => item.scene)));
  const statusOptions = Array.from(new Set((data ?? []).map((item) => item.status)));
  const providerOptions = Array.from(new Set((data ?? []).map((item) => parseProviderChain(item.provider).primary)));

  return (
    <div className={`workspace-grid workspace-grid--history ${expanded ? 'is-expanded' : ''}`}>
      <div className="panel workspace-panel workspace-panel--list">
        <div className="section-header workspace-header">
          <div><h3>智能分析执行历史</h3><span className="muted-inline">支持按场景、状态、模型和对象筛选，并查看降级情况与写回对象</span></div>
          <div className="workspace-actions"><StatusBadge value={filteredData.length} tone="info" /><button className="ghost-btn" type="button" onClick={resetLayout} disabled={!expanded}>恢复默认尺寸</button></div>
        </div>
        <div className="action-row"><button className="ghost-btn" type="button" onClick={() => setQuickFilter('all')}>全部</button><button className="ghost-btn" type="button" onClick={() => setQuickFilter('failed')}>只看失败</button><button className="ghost-btn" type="button" onClick={() => setQuickFilter('degraded')}>只看降级</button></div>
        <div className="action-row">
          <select value={sceneFilter} onChange={(event) => setSceneFilter(event.target.value)}><option value="all">全部场景</option>{sceneOptions.map((scene) => <option key={scene} value={scene}>{getSceneLabel(scene)}</option>)}</select>
          <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}><option value="all">全部状态</option>{statusOptions.map((status) => <option key={status} value={status}>{getStatusLabel(status)}</option>)}</select>
          <select value={providerFilter} onChange={(event) => setProviderFilter(event.target.value)}><option value="all">全部模型</option>{providerOptions.map((provider) => <option key={provider} value={provider}>{getProviderLabel(provider)}</option>)}</select>
          <input value={entityFilter} onChange={(event) => setEntityFilter(event.target.value)} placeholder="筛选对象编号" />
        </div>
        <div className="list-table scroll-area workspace-scroll workspace-scroll--list">
          {filteredData.map((item, index) => {
            const providerMeta = parseProviderChain(item.provider);
            return <button className="list-button" key={index} onClick={() => handleSelectTask(item.task_id)}><div className={`list-row dense ${selectedTaskId === item.task_id ? 'is-selected' : ''}`}><strong>{getSceneLabel(item.scene)}</strong><span>{providerMeta.display}</span><span><StatusBadge value={getStatusLabel(item.status)} tone={getExecutionTone(item.status, item.provider)} /></span><span><StatusBadge value={providerMeta.isFallback ? '已降级' : getExecutionModeLabel(providerMeta.primary)} tone={getExecutionTone(item.status, item.provider)} /></span><span>{item.entity_id || '-'}</span><span>{item.created_at}</span><span>{item.summary}</span></div></button>;
          })}
        </div>
      </div>
      <div className="panel workspace-panel workspace-panel--detail">
        <div className="section-header workspace-header">
          <div><h3>历史详情</h3><span className="muted-inline">详情中可查看执行链路、写回对象、降级信息与结构化结果</span></div>
          <div className="workspace-actions">{selectedTaskId ? <StatusBadge value="已联动" tone="success" /> : <StatusBadge value="待选择" tone="neutral" />}<button className="ghost-btn" type="button" onClick={resetLayout} disabled={!expanded}>收起到默认视图</button></div>
        </div>
        {detailQuery.data ? <div className="page-stack scroll-area workspace-scroll workspace-scroll--detail"><div className="detail-grid"><div><strong>任务编号</strong><span>{detailQuery.data.task_id}</span></div><div><strong>状态</strong><span><StatusBadge value={getStatusLabel(detailQuery.data.status)} tone={getExecutionTone(detailQuery.data.status, detailQuery.data.provider)} /></span></div><div><strong>模型服务</strong><span>{selectedProviderMeta?.display ?? getProviderLabel(detailQuery.data.provider)}</span></div><div><strong>分析场景</strong><span>{getSceneLabel(detailQuery.data.scene)}</span></div><div><strong>对象编号</strong><span>{detailQuery.data.entity_id || '-'}</span></div><div><strong>写回对象</strong><span>{writebackEntries.length ? writebackObjectLabel : '无结构化写回'}</span></div><div><strong>执行耗时</strong><span>{detailQuery.data.duration_ms ?? 0} 毫秒</span></div><div><strong>完成时间</strong><span>{detailQuery.data.completed_at ?? '-'}</span></div></div><div className="panel-grid two-columns"><div className="detail-block"><strong>执行链路</strong><div className="detail-grid"><div><strong>主模型</strong><span>{selectedProviderMeta?.primary ? getProviderLabel(selectedProviderMeta.primary) : '-'}</span></div><div><strong>执行模式</strong><span><StatusBadge value={selectedProviderMeta?.isFallback ? '降级执行' : detailQuery.data.status === 'failed' ? '失败结束' : '正常执行'} tone={detailQuery.data.status === 'failed' ? 'danger' : selectedProviderMeta?.isFallback ? 'warning' : 'success'} /></span></div><div><strong>是否使用模拟模型</strong><span><StatusBadge value={selectedProviderMeta?.usedMock ? '是' : '否'} tone={selectedProviderMeta?.usedMock ? 'warning' : 'info'} /></span></div><div><strong>回退目标</strong><span>{selectedProviderMeta?.fallback ? getProviderLabel(selectedProviderMeta.fallback) : '-'}</span></div></div></div><div className="detail-block"><strong>摘要</strong><div className="detail-content">{detailQuery.data.summary}</div></div></div>{detailQuery.data.status === 'failed' || detailQuery.data.provider.includes('mock') ? <div className="detail-block"><strong>{detailQuery.data.status === 'failed' ? '失败原因' : '降级说明'}</strong><div className="detail-content">{detailQuery.data.error_message || (detailQuery.data.provider.includes('mock') ? '当前执行链路包含模拟模型兜底，建议结合主模型状态一起排查本次结果来源。' : '本次任务执行失败，请结合后端日志进一步排查。')}</div></div> : null}{knowledgeSources.length ? <div className="detail-block detail-block--scroll"><strong>知识来源</strong><div className="scroll-area scroll-area--sm"><ul>{knowledgeSources.map((item, index) => <li key={index}>{formatDisplayValue(item.doc_name ?? '-')} / {formatDisplayValue(item.domain_type ?? '-')} / {formatDisplayValue(item.version_no ?? '-')}</li>)}</ul></div></div> : null}<div className="detail-block detail-block--scroll"><strong>写回结果</strong>{writebackEntries.length ? <div className="scroll-area scroll-area--md"><ul>{writebackEntries.map(([key, value]) => <li key={key}>{getWritebackFieldLabel(key)}：{formatDisplayValue(value)}</li>)}</ul></div> : <div className="detail-content">本次历史记录没有检测到结构化写回字段。</div>}</div><div className="detail-block detail-block--scroll"><strong>洞察</strong><div className="scroll-area scroll-area--md"><ul>{detailQuery.data.insights.map((item, index) => <li key={index}>{item.title}：{item.content}（{Math.round(item.confidence * 100)}%）</li>)}</ul></div></div><div className="detail-block detail-block--scroll"><strong>推荐建议</strong><div className="scroll-area scroll-area--sm"><ul>{detailQuery.data.recommendations.map((item, index) => <li key={index}>{item}</li>)}</ul></div></div><div className="detail-block detail-block--scroll"><strong>下一步动作</strong><div className="scroll-area scroll-area--sm"><ul>{detailQuery.data.next_actions.map((item, index) => <li key={index}>{item}</li>)}</ul></div></div><div className="detail-block detail-block--scroll"><strong>证据与依据</strong><div className="scroll-area scroll-area--sm"><ul>{detailQuery.data.evidence.map((item, index) => <li key={index}>{item}</li>)}</ul></div></div></div> : <div className="empty-state workspace-empty-state"><strong>选择左侧一条智能分析执行记录</strong><span>选中后将自动切换到联动展开模式，左侧列表与右侧详情会同步增高；你也可以一键恢复到默认板块大小。</span></div>}
      </div>
    </div>
  );
}
