import { useEffect, useMemo, useState } from 'react';

import { APIError, fetcher, poster } from '../lib/api';
import type { AIExecutionResult } from '../types';
import { AlertBanner } from './AlertBanner';
import { StatusBadge } from './StatusBadge';

type SceneMeta = { label: string; subtitle: string; insightTitle: string; recommendationTitle: string; actionTitle: string; evidenceTitle: string; metricLabels: [string, string, string, string]; };
type HighlightItem = { label: string; value: string };

const FIELD_LABELS: Record<string, string> = {
  project_name: '项目名称',
  industry_code: '行业编码',
  bid_type: '招采类型',
  risk_level: '风险等级',
  proposal_status: '方案状态',
  approval_status: '审批状态',
  version_no: '版本号',
  owner_user_id: '负责人',
  requirement_json: '招标需求解析',
  scoring_rule_json: '评分规则',
  generated_outline_uri: '方案大纲',
  technical_draft_uri: '技术方案草稿',
  commercial_draft_uri: '商务方案草稿',
  ai_lead_score: '线索评分',
  ai_priority_level: '优先级',
  ai_maturity_level: '成熟度',
  ai_next_action: '下一步动作',
  lead_status: '线索状态',
  supplier_status: '供应商状态',
  total_score: '综合得分',
  cooperation_suggestion: '合作建议',
  recommended_supplier_id: '推荐供应商',
  recommended_quote_id: '推荐报价',
  purchase_request_id: '采购申请',
  rfq_id: '询价单',
  generated_outline_written: '方案大纲已写回',
  technical_draft_written: '技术方案已写回',
  commercial_draft_written: '商务方案已写回',
  proposal_id: '方案项目',
  supplier_id: '供应商',
  writeback: '写回结果',
  knowledge_sources: '知识来源',
};

const VALUE_LABELS: Record<string, string> = {
  lead_followup: '线索跟进',
  proposal_generation: '方案生成',
  supplier_assessment: '供应商评估',
  procurement_analysis: '采购分析',
  ops_analysis: '运营分析',
  rfp: '招标文件项目',
  tender: '招标项目',
  draft: '草稿',
  reviewing: '评审中',
  approved: '已通过',
  generated: '已生成',
  rfp_parsed: '已解析',
  rejected: '已拒绝',
  high: '高',
  medium: '中',
  low: '低',
  pending: '待处理',
  queued: '排队中',
  running: '执行中',
  completed: '执行成功',
  degraded: '降级完成',
  failed: '执行失败',
  true: '是',
  false: '否',
  aliyun_qwen: '阿里云通义千问',
  mock: '模拟模型',
  openai: 'OpenAI',
  azure_openai: 'Azure OpenAI',
  local: '本地模型',
};

function getSceneGlyph(scene: string) {
  const mapping: Record<string, string> = { lead_followup: '线', proposal_generation: '案', supplier_assessment: '供', procurement_analysis: '采', ops_analysis: '营' };
  return mapping[scene] ?? '智';
}
function getSceneMeta(scene: string): SceneMeta {
  const mapping: Record<string, SceneMeta> = {
    lead_followup: { label: '线索跟进', subtitle: '围绕客户意向、推进节奏与下一次触达动作形成销售跟进判断', insightTitle: '客户判断', recommendationTitle: '跟进建议', actionTitle: '下一次销售动作', evidenceTitle: '判断依据', metricLabels: ['客户洞察', '跟进建议', '待办动作', '判断依据'] },
    proposal_generation: { label: '方案生成', subtitle: '围绕方案结构、风险条款与编制动作形成售前方案建议', insightTitle: '方案洞察', recommendationTitle: '编制建议', actionTitle: '方案推进动作', evidenceTitle: '条款与依据', metricLabels: ['结构洞察', '编制建议', '推进动作', '风险依据'] },
    supplier_assessment: { label: '供应商评估', subtitle: '围绕合作价值、风险等级与治理动作形成供应商合作判断', insightTitle: '合作洞察', recommendationTitle: '合作建议', actionTitle: '治理动作', evidenceTitle: '评估依据', metricLabels: ['评估洞察', '合作建议', '治理动作', '评估依据'] },
    procurement_analysis: { label: '采购分析', subtitle: '围绕报价结构、推荐供应商与谈判动作形成采购决策建议', insightTitle: '采购判断', recommendationTitle: '采购建议', actionTitle: '谈判与定标动作', evidenceTitle: '比价依据', metricLabels: ['采购洞察', '采购建议', '推进动作', '比价依据'] },
    ops_analysis: { label: '运营分析', subtitle: '围绕运行质量、异常信号与优化动作形成平台级运营结论', insightTitle: '运营洞察', recommendationTitle: '优化建议', actionTitle: '重点运营动作', evidenceTitle: '风险与依据', metricLabels: ['运营洞察', '优化建议', '重点动作', '风险依据'] },
  };
  return mapping[scene] ?? mapping.ops_analysis;
}
function getProviderDisplay(provider: string) {
  return String(provider ?? '')
    .split('->')
    .map((item) => VALUE_LABELS[item.trim()] ?? item.trim())
    .filter(Boolean)
    .join(' → ') || '-';
}
function getStatusLabel(status: string) { const mapping: Record<string, string> = { queued: '排队中', running: '执行中', completed: '执行成功', degraded: '降级完成', failed: '执行失败' }; return mapping[String(status).toLowerCase()] ?? status; }
function getProgressMessage(status: string) { const mapping: Record<string, string> = { queued: '任务已创建，正在进入执行队列。', running: '正在调用模型并写回业务对象，请稍候。', completed: '任务已完成，结果与写回信息已生成。', degraded: '主链路异常，系统已降级并生成兜底结果。', failed: '任务执行失败，请检查错误信息或稍后重试。' }; return mapping[String(status).toLowerCase()] ?? '任务状态已更新。'; }
function getFieldLabel(key: string) { return FIELD_LABELS[key] ?? key.replaceAll('_', ' '); }
function formatDisplayValue(value: unknown): string {
  if (value === null || value === undefined || value === '') return '-';
  if (typeof value === 'boolean') return value ? '是' : '否';
  if (typeof value === 'number') return String(value);
  const text = String(value).trim();
  return VALUE_LABELS[text] ?? text;
}
function getWritebackEntries(context: Record<string, unknown>) { const writeback = context.writeback; return !writeback || typeof writeback !== 'object' || Array.isArray(writeback) ? [] as Array<[string, unknown]> : Object.entries(writeback).filter(([, value]) => value !== undefined && value !== null && value !== ''); }
function getKnowledgeSources(context: Record<string, unknown>) { const sources = context.knowledge_sources; return Array.isArray(sources) ? sources as Array<Record<string, unknown>> : []; }
function getWritebackSummary(scene: string, entries: Array<[string, unknown]>) {
  if (!entries.length) return '本次执行以分析结果展示为主，暂无结构化写回。';
  const labels: Record<string, string> = { lead_followup: '已回写线索评分、优先级和跟进结果。', proposal_generation: '已回写方案草稿、版本号和方案状态。', supplier_assessment: '已生成供应商评估结果并更新风险结论。', procurement_analysis: '已回写询价推荐结果并联动采购状态。', ops_analysis: '已生成运营分析结果，当前场景默认不直接写回业务对象。' };
  return labels[scene] ?? '已完成本次 AI 结构化写回。';
}
function pickWritebackValue(entries: Array<[string, unknown]>, key: string) { return entries.find(([entryKey]) => entryKey === key)?.[1]; }
function summarizeValue(value: unknown): string {
  const text = formatDisplayValue(value);
  return text.length > 36 ? `${text.slice(0, 36)}...` : text;
}
function getSceneHighlights(scene: string, result: AIExecutionResult, writebackEntries: Array<[string, unknown]>): HighlightItem[] {
  const context = result.context;
  const highlights: Record<string, HighlightItem[]> = {
    lead_followup: [{ label: '优先级', value: String(pickWritebackValue(writebackEntries, 'ai_priority_level') ?? context.priority ?? '-') }, { label: '线索评分', value: String(pickWritebackValue(writebackEntries, 'ai_lead_score') ?? context.ai_lead_score ?? '-') }, { label: '跟进状态', value: String(pickWritebackValue(writebackEntries, 'lead_status') ?? context.lead_status ?? '-') }, { label: '下一步', value: String(result.next_actions[0] ?? context.ai_next_action ?? '-') }],
    proposal_generation: [{ label: '方案状态', value: String(pickWritebackValue(writebackEntries, 'proposal_status') ?? context.proposal_status ?? '-') }, { label: '版本号', value: String(pickWritebackValue(writebackEntries, 'version_no') ?? context.version_no ?? '-') }, { label: '风险等级', value: String(context.risk_level ?? '-') }, { label: '首要建议', value: String(result.recommendations[0] ?? '-') }],
    supplier_assessment: [{ label: '风险等级', value: String(pickWritebackValue(writebackEntries, 'risk_level') ?? context.latest_risk_level ?? '-') }, { label: '总分', value: String(pickWritebackValue(writebackEntries, 'total_score') ?? context.latest_evaluation_score ?? '-') }, { label: '供应商状态', value: String(pickWritebackValue(writebackEntries, 'supplier_status') ?? context.supplier_status ?? '-') }, { label: '合作建议', value: String(pickWritebackValue(writebackEntries, 'cooperation_suggestion') ?? result.recommendations[0] ?? '-') }],
    procurement_analysis: [{ label: '推荐供应商', value: String(pickWritebackValue(writebackEntries, 'recommended_supplier_id') ?? context.recommended_supplier ?? '-') }, { label: '推荐报价', value: String(pickWritebackValue(writebackEntries, 'recommended_quote_id') ?? '-') }, { label: '风险等级', value: String(pickWritebackValue(writebackEntries, 'risk_level') ?? '-') }, { label: '首要动作', value: String(result.next_actions[0] ?? '-') }],
    ops_analysis: [{ label: '服务状态', value: String(context.service_status ?? '-') }, { label: '请求量', value: String(context.request_count ?? '-') }, { label: '错误数', value: String(context.error_count ?? '-') }, { label: '降级数', value: String(context.degraded_count ?? '-') }],
  };
  return (highlights[scene] ?? []).filter((item) => item.value !== '' && item.value !== 'undefined');
}

export function AIActionPanel(props: { title: string; scene: string; entityId?: string; context?: Record<string, unknown>; onExecuted?: (result: AIExecutionResult) => void; onStatusChange?: (status: string) => void; }) {
  const [result, setResult] = useState<AIExecutionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [taskId, setTaskId] = useState('');
  const [expanded, setExpanded] = useState(false);
  const [slowHint, setSlowHint] = useState(false);
  const contextEntries = Object.entries(props.context ?? {}).filter(([, value]) => value !== undefined && value !== null && value !== '');
  const sceneMeta = getSceneMeta(props.scene);
  const writebackEntries = result ? getWritebackEntries(result.context) : [];
  const knowledgeSources = result ? getKnowledgeSources(result.context) : [];
  const keyContextEntries = useMemo(() => contextEntries.slice(0, 5), [contextEntries]);
  const sceneHighlights = result ? getSceneHighlights(props.scene, result, writebackEntries) : [];

  useEffect(() => {
    if (!loading) { setSlowHint(false); return; }
    const timer = window.setTimeout(() => setSlowHint(true), 20000);
    return () => window.clearTimeout(timer);
  }, [loading]);

  useEffect(() => {
    if (!taskId) return;
    const timer = window.setInterval(async () => {
      try {
        const task = await fetcher<AIExecutionResult>(`/ai/tasks/${taskId}`);
        setResult(task);
        props.onStatusChange?.(task.status);
        if (!['queued', 'running'].includes(task.status)) { window.clearInterval(timer); setLoading(false); props.onExecuted?.(task); }
      } catch (pollError) {
        window.clearInterval(timer); setLoading(false); props.onStatusChange?.('failed');
        if (pollError instanceof APIError) setError(`${pollError.code}: ${pollError.message}`); else setError('智能任务状态查询失败，请稍后重试。');
      }
    }, 1500);
    return () => window.clearInterval(timer);
  }, [taskId, props]);

  const run = async () => {
    setLoading(true); setError(''); setResult(null); setSlowHint(false); props.onStatusChange?.('queued');
    try { const queued = await poster<AIExecutionResult>('/ai/tasks', { scene: props.scene, entity_id: props.entityId, context: props.context ?? {} }); setTaskId(queued.task_id); setResult(queued); props.onStatusChange?.(queued.status); }
    catch (actionError) { setLoading(false); props.onStatusChange?.('failed'); if (actionError instanceof APIError) setError(`${actionError.code}: ${actionError.message}`); else setError('智能分析执行失败，请稍后重试。'); }
  };

  return <div className={`panel ai-panel ai-panel--${props.scene} page-stack`}>{error ? <AlertBanner title="智能分析执行失败" message={error} tone="danger" /> : null}{loading && slowHint ? <AlertBanner title="智能分析耗时较长" message="任务已运行超过 20 秒，可能卡在模型返回解析或写回阶段。若长时间无结果，请稍后重试，并查看后端日志中的 traceback。" tone="warning" /> : null}{result?.degraded ? <AlertBanner title="已自动降级为兜底结果" message={result.error_message || '当前模型调用失败，系统已切换为兜底结果以保证页面可继续使用。'} tone="warning" /> : null}<div className="section-header ai-panel__header"><div className="ai-panel__title"><span className="ai-panel__glyph">{getSceneGlyph(props.scene)}</span><div><h3>{props.title}</h3><span className="muted-inline">{sceneMeta.subtitle}</span></div></div><div className="workspace-actions"><button className="ghost-btn" type="button" onClick={() => setExpanded((prev) => !prev)}>{expanded ? '收起详情' : '展开详情'}</button><button className="primary-btn" onClick={run} disabled={loading}>{loading ? '执行中...' : '运行智能分析'}</button></div></div><div className="detail-block ai-panel__overview"><strong>执行概览</strong><div className="hero-panel__meta"><span>分析场景：{sceneMeta.label}</span><span>当前对象：{props.entityId ?? '-'}</span><span>上下文字段数：{contextEntries.length}</span><span>任务编号：{result?.task_id ?? '-'}</span></div><div className="action-row">{result ? <><StatusBadge value={getStatusLabel(result.status)} /><span>{getProgressMessage(result.status)}</span></> : <span>点击“运行智能分析”后，系统将生成本次分析结果。</span>}</div>{keyContextEntries.length ? <div className="list-table">{keyContextEntries.map(([key, value]) => <div className="list-row" key={key}><strong>{getFieldLabel(key)}</strong><span>{summarizeValue(value)}</span><span>关键上下文</span></div>)}</div> : null}</div>{result ? <div className="page-stack"><div className="ai-highlight-grid">{sceneHighlights.map((item) => <div className="ai-highlight-card" key={item.label}><span className="ai-highlight-card__label">{item.label}</span><strong className="ai-highlight-card__value">{item.value}</strong></div>)}</div><div className="panel-grid two-columns"><div className="detail-block ai-summary-card"><strong>执行摘要</strong><div className="hero-panel__meta"><span>模型服务：{getProviderDisplay(result.provider)}</span><span>执行智能体：{sceneMeta.label}</span><span>耗时：{result.duration_ms} 毫秒</span></div><p>{result.summary || '任务已创建，等待执行结果。'}</p></div><div className="detail-block"><strong>写回结果</strong><p>{getWritebackSummary(props.scene, writebackEntries)}</p>{writebackEntries.length ? <div className="ai-writeback-tags">{writebackEntries.slice(0, 4).map(([key, value]) => <span className="ai-writeback-tag" key={key}><strong>{getFieldLabel(key)}</strong>{formatDisplayValue(value)}</span>)}</div> : <div className="empty-state"><strong>暂无结构化写回</strong><span>当前执行已生成分析结果，但还没有回写到具体业务字段。</span></div>}</div></div><div className="panel-grid two-columns"><div className="detail-block"><strong>{sceneMeta.recommendationTitle}</strong><div className="list-table">{result.recommendations.slice(0, 2).map((item, index) => <div className="list-row" key={index}><strong>建议 {index + 1}</strong><span>{item}</span><span>{sceneMeta.label}</span></div>)}</div></div><div className="detail-block"><strong>{sceneMeta.actionTitle}</strong><div className="list-table">{result.next_actions.slice(0, 2).map((item, index) => <div className="list-row" key={index}><strong>动作 {index + 1}</strong><span>{item}</span><span><StatusBadge value={getStatusLabel(result.status)} /></span></div>)}</div></div></div>{expanded ? <div className="page-stack"><div className="panel-grid two-columns"><div className="detail-block"><strong>{sceneMeta.insightTitle}</strong><div className="list-table">{result.insights.map((item, index) => <div className="list-row" key={index}><strong>{item.title}</strong><span>{item.content}</span><span>可信度 {(item.confidence * 100).toFixed(0)}%</span></div>)}</div></div><div className="detail-block"><strong>{sceneMeta.evidenceTitle}</strong><ul>{result.evidence.map((item, index) => <li key={index}>{item}</li>)}</ul></div></div>{knowledgeSources.length ? <div className="detail-block"><strong>知识来源</strong><div className="list-table">{knowledgeSources.map((item, index) => <div className="list-row" key={index}><strong>{formatDisplayValue(item.doc_name ?? '-')}</strong><span>{formatDisplayValue(item.domain_type ?? '-')}</span><span>{formatDisplayValue(item.version_no ?? '-')}</span></div>)}</div></div> : null}<div className="detail-block"><strong>完整执行上下文</strong>{contextEntries.length ? <div className="list-table">{contextEntries.map(([key, value]) => <div className="list-row" key={key}><strong>{getFieldLabel(key)}</strong><span>{formatDisplayValue(value)}</span><span>上下文</span></div>)}</div> : <div className="empty-state"><strong>暂无附加上下文</strong><span>当前场景没有额外上下文。</span></div>}</div></div> : null}</div> : <div className="empty-state"><strong>等待执行智能分析</strong><span>点击“运行智能分析”后，将展示与当前场景对应的摘要、建议、动作与写回结果。更多细节可按需展开查看。</span></div>}</div>;
}
