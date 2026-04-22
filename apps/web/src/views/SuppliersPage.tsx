import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { AIActionPanel } from '../components/AIActionPanel';
import { AlertBanner } from '../components/AlertBanner';
import { PageHeader } from '../components/PageHeader';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { SupplierCreateForm } from '../components/SupplierCreateForm';
import { APIError, deleter, fetcher, poster } from '../lib/api';
import type { SupplierRecord } from '../types';

export function SuppliersPage() {
  const suppliers = useQuery({ queryKey: ['suppliers'], queryFn: () => fetcher<Array<Record<string, unknown>>>('/suppliers') });
  const evaluations = useQuery({ queryKey: ['supplier-evaluations'], queryFn: () => fetcher<Array<Record<string, unknown>>>('/suppliers/evaluations') });
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [editing, setEditing] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const selected = useMemo(() => suppliers.data?.find((item) => String(item.id) === selectedId) ?? suppliers.data?.[0] ?? null, [selectedId, suppliers.data]) as SupplierRecord | null;
  const selectedEvaluations = useMemo(() => (evaluations.data ?? []).filter((item) => String(item.supplier_id) === String(selected?.id ?? '')), [evaluations.data, selected?.id]);
  const supplierCount = suppliers.data?.length ?? 0;
  const evaluationCount = evaluations.data?.length ?? 0;
  const strategicCount = (suppliers.data ?? []).filter((item) => Boolean(item.strategic_supplier_flag)).length;
  const highRiskCount = (evaluations.data ?? []).filter((item) => String(item.risk_level).toLowerCase() === 'high').length;
  const refreshAll = async () => { await Promise.all([suppliers.refetch(), evaluations.refetch()]); };
  const updateSupplierStatus = async (supplierStatus: string) => {
    if (!selected) return; setSubmitting(true); setMessage(''); setError('');
    try { await poster(`/suppliers/${selected.id}/status`, { supplier_status: supplierStatus }); setMessage(`供应商状态已更新为 ${supplierStatus}。`); await refreshAll(); }
    catch (submitError) { if (submitError instanceof APIError) setError(`${submitError.code}: ${submitError.message}`); else setError('供应商状态更新失败，请稍后重试。'); }
    finally { setSubmitting(false); }
  };
  const removeSupplier = async () => {
    if (!selected) return;
    if (!window.confirm(`确认删除供应商「${selected.supplier_name}」吗？其评估记录也会一并删除。`)) return;
    setSubmitting(true); setMessage(''); setError('');
    try { await deleter(`/suppliers/${selected.id}`); setMessage('供应商已删除。'); setSelectedId(null); setEditing(false); await refreshAll(); }
    catch (submitError) { if (submitError instanceof APIError) setError(`${submitError.code}: ${submitError.message}`); else setError('供应商删除失败，请稍后重试。'); }
    finally { setSubmitting(false); }
  };
  return (
    <div className="page-stack">
      <PageHeader title="供应商评估智能体" description="围绕供应商主数据、评估结果、风险信号与合作建议，构建更完整的供应商分析与治理工作台。" />
      {message ? <AlertBanner title="操作成功" message={message} tone="success" /> : null}
      {error ? <AlertBanner title="操作失败" message={error} tone="danger" /> : null}
      <section className="hero-panel"><div className="hero-panel__main"><div className="hero-panel__eyebrow">供应商智能分析</div><h3>把供应商画像、评估结果、风险等级与合作策略统一沉淀到一个管理界面里</h3><p>面向采购经理、供应商管理负责人和品类负责人，统一查看供应商状态、评估得分、风险等级和合作建议，提升供应商管理的透明度与治理能力。</p><div className="hero-panel__meta"><span>多维度评分</span><span>风险与合作建议联动</span><span>支持智能评估辅助</span></div></div><div className="hero-panel__side"><div className="hero-kpi success"><strong>{supplierCount}</strong><span>供应商总数</span></div><div className="hero-kpi warning"><strong>{highRiskCount}</strong><span>高风险评估记录</span></div></div></section>
      <section className="stats-grid"><StatCard title="供应商总量" value={supplierCount} hint="当前供应商池" /><StatCard title="评估记录" value={evaluationCount} hint="累计评估次数" /><StatCard title="战略供应商" value={strategicCount} hint="重点合作对象" tone="success" /><StatCard title="高风险评估" value={highRiskCount} hint="建议优先复核" tone="warning" /></section>
      <div className="panel"><div className="section-header"><div><h3>新建供应商</h3><span className="muted-inline">创建后可进入评估、对比和合作策略分析流程</span></div></div><SupplierCreateForm onCreated={() => void suppliers.refetch()} /></div>
      <div className="panel-grid two-columns"><div className="panel"><div className="section-header"><div><h3>供应商列表</h3><span className="muted-inline">快速查看分类、状态、资质与区域分布</span></div></div><div className="list-table">{(suppliers.data ?? []).map((item) => <button className={`list-button ${selected && String(selected.id) === String(item.id) ? 'is-selected' : ''}`} key={String(item.id)} onClick={() => { setSelectedId(String(item.id)); setEditing(false); }}><div className="list-row dense"><strong>{String(item.supplier_name)}</strong><span>{String(item.supplier_category)}</span><span><StatusBadge value={String(item.supplier_status)} /></span><span>{String(item.qualification_level)}</span><span>{String(item.region_code)}</span></div></button>)}</div></div><div className="panel"><div className="section-header"><div><h3>供应商详情</h3><span className="muted-inline">查看基础画像与评估结果，形成合作判断</span></div>{selected ? <div className="workspace-actions"><button className="ghost-btn" type="button" onClick={() => setEditing((prev) => !prev)}>{editing ? '收起编辑' : '编辑供应商'}</button><button className="ghost-btn" type="button" disabled={submitting} onClick={() => void updateSupplierStatus('active')}>回退为启用</button><button className="ghost-btn" type="button" disabled={submitting} onClick={() => void removeSupplier()}>删除供应商</button></div> : null}</div>{selected ? <div className="page-stack">{editing ? <div className="detail-block"><strong>编辑供应商</strong><SupplierCreateForm initialSupplier={selected} onCreated={() => { setEditing(false); void refreshAll(); }} onCancelled={() => setEditing(false)} /></div> : null}<div className="detail-block"><strong>状态调整</strong><div className="action-row"><button className="ghost-btn" type="button" disabled={submitting} onClick={() => void updateSupplierStatus('active')}>转为启用</button><button className="ghost-btn" type="button" disabled={submitting} onClick={() => void updateSupplierStatus('inactive')}>转为停用</button><button className="ghost-btn" type="button" disabled={submitting} onClick={() => void updateSupplierStatus('suspended')}>转为暂停合作</button><button className="ghost-btn" type="button" disabled={submitting} onClick={() => void updateSupplierStatus('archived')}>转为归档</button></div></div><div className="panel-grid two-columns"><div className="detail-block"><strong>供应商画像</strong><div className="detail-grid"><div><strong>名称</strong><span>{String(selected.supplier_name)}</span></div><div><strong>分类</strong><span>{String(selected.supplier_category)}</span></div><div><strong>状态</strong><span><StatusBadge value={String(selected.supplier_status)} /></span></div><div><strong>资质等级</strong><span>{String(selected.qualification_level)}</span></div><div><strong>区域编码</strong><span>{String(selected.region_code)}</span></div><div><strong>战略供应商</strong><span><StatusBadge value={selected.strategic_supplier_flag ? '启用' : '普通'} /></span></div></div></div><div className="detail-block"><strong>合作判断</strong><div className="signal-list"><div className="signal-item"><strong>当前重点</strong><span>先结合供应商状态、资质等级和最近一次评估结果判断是否适合继续扩大合作范围。</span></div><div className="signal-item"><strong>治理建议</strong><span>高风险供应商建议优先安排复评、整改跟踪或替代资源预案，避免关键采购环节受影响。</span></div><div className="signal-item"><strong>合作策略</strong><span>对表现稳定、战略价值高的供应商，可纳入重点合作池并沉淀长期协同机制。</span></div></div></div></div><div className="detail-block"><strong>评估结果</strong><div className="list-table">{selectedEvaluations.map((item, index) => <div className="list-row dense" key={index}><strong>{String(item.evaluation_period)}</strong><span>总分 {String(item.total_score)}</span><span><StatusBadge value={String(item.risk_level)} /></span><span>{String(item.cooperation_suggestion)}</span><span>{String(item.reviewer_user_id ?? '-')}</span></div>)}</div></div></div> : <div className="empty-state"><strong>请选择一个供应商</strong><span>从左侧选择供应商后，可查看其基础信息、评估得分与合作建议。</span></div>}</div></div>
      <AIActionPanel title="智能供应商评估助手" scene="supplier_assessment" entityId={selected ? String(selected.id) : undefined} context={{ supplier_name: selected?.supplier_name, supplier_code: selected?.supplier_code, supplier_category: selected?.supplier_category, qualification_level: selected?.qualification_level, supplier_status: selected?.supplier_status, region_code: selected?.region_code, major_products: selected?.major_products, contact_person: selected?.contact_person, contact_phone: selected?.contact_phone, settlement_terms: selected?.settlement_terms, strategic_supplier_flag: selected?.strategic_supplier_flag, evaluation_count: selectedEvaluations.length, latest_evaluation_score: selectedEvaluations[0]?.total_score, latest_risk_level: selectedEvaluations[0]?.risk_level, latest_cooperation_suggestion: selectedEvaluations[0]?.cooperation_suggestion }} />
    </div>
  );
}
