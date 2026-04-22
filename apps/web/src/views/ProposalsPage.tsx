import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { AIActionPanel } from '../components/AIActionPanel';
import { AlertBanner } from '../components/AlertBanner';
import { PageHeader } from '../components/PageHeader';
import { ProposalCreateForm } from '../components/ProposalCreateForm';
import { StatCard } from '../components/StatCard';
import { StatusBadge } from '../components/StatusBadge';
import { APIError, deleter, fetcher, poster, posterForm } from '../lib/api';

const statusLabel = (s: string) => ({ draft: '草稿', reviewing: '评审中', approved: '已通过', generated: '已生成', rfp_parsed: '已解析', rejected: '已拒绝' }[s] ?? s);
const bidTypeLabel = (s: string) => ({ rfp: '招标文件项目', tender: '招标项目' }[s] ?? s);
const textOf = (v: unknown, d: string) => String(v ?? '').trim() || d;

function DetailCard({ title, tip, text, onOpen, badge }: { title: string; tip: string; text: string; onOpen: () => void; badge?: { value: string; tone: 'success' | 'warning' | 'neutral' } }) {
  return <div className="detail-block detail-block--scroll detail-block--rich"><div className="detail-block__header"><div><strong>{title}</strong><span className="muted-inline">{tip}</span></div><div className="workspace-actions">{badge ? <StatusBadge value={badge.value} tone={badge.tone} /> : null}<button className="ghost-btn" type="button" onClick={onOpen}>展开查看</button></div></div><div className="detail-content detail-content--rich">{text}</div></div>;
}
function DetailModal({ title, tip, text, onClose }: { title: string; tip: string; text: string; onClose: () => void }) {
  return <div className="proposal-modal-backdrop" onClick={onClose}><div className="proposal-modal" role="dialog" aria-modal="true" aria-label={title} onClick={(e) => e.stopPropagation()}><div className="proposal-modal__header"><div><div className="hero-panel__eyebrow">方案详情展开阅读</div><h3>{title}</h3><p>{tip}</p></div><button className="ghost-btn" type="button" onClick={onClose}>关闭</button></div><div className="proposal-modal__content scroll-area">{text}</div></div></div>;
}

export function ProposalsPage() {
  const query = useQuery({ queryKey: ['proposals'], queryFn: () => fetcher<Array<Record<string, unknown>>>('/proposals') });
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [rfpContent, setRfpContent] = useState('');
  const [rfpFile, setRfpFile] = useState<File | null>(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [expanded, setExpanded] = useState(false);
  const [editing, setEditing] = useState(false);
  const [modal, setModal] = useState<{ title: string; tip: string; text: string } | null>(null);
  const selected = useMemo(() => query.data?.find((i) => String(i.id) === selectedId) ?? query.data?.[0] ?? null, [query.data, selectedId]);
  const projectCount = query.data?.length ?? 0;
  const highRiskCount = (query.data ?? []).filter((i) => String(i.risk_level).toLowerCase() === 'high').length;
  const pendingApprovalCount = (query.data ?? []).filter((i) => String(i.approval_status).toLowerCase() !== 'approved').length;
  const requirement = textOf(selected?.requirement_json, '待生成需求结构化结果。');
  const scoring = textOf(selected?.scoring_rule_json, '待生成评分办法。');
  const technical = textOf(selected?.technical_draft_uri, '待生成技术方案草稿。');
  const commercial = textOf(selected?.commercial_draft_uri, '待生成商务方案草稿。');
  const outline = textOf(selected?.generated_outline_uri, '待生成方案大纲。');
  const proposalStatus = String(selected?.proposal_status ?? 'draft');
  const technicalReady = Boolean(String(selected?.technical_draft_uri ?? '').trim());
  const commercialReady = Boolean(String(selected?.commercial_draft_uri ?? '').trim());
  const outlineReady = Boolean(String(selected?.generated_outline_uri ?? '').trim());
  const runAction = async (action: () => Promise<void>, ok: string) => {
    setSubmitting(true); setMessage(''); setError('');
    try { await action(); await query.refetch(); setMessage(ok); }
    catch (e) { setError(e instanceof APIError ? `${e.code}: ${e.message}` : '方案动作执行失败，请稍后重试。'); }
    finally { setSubmitting(false); }
  };
  const submitRfp = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!selected) return;
    if (!rfpFile && !rfpContent.trim()) return setError('请先选择一个本地文件，或补充粘贴招标文件内容。');
    await runAction(async () => {
      const form = new FormData();
      if (rfpFile) form.append('file', rfpFile);
      form.append('rfp_content', rfpContent);
      await posterForm(`/proposals/${String(selected.id)}/rfp`, form);
      setRfpFile(null); setRfpContent('');
    }, '招标文件内容已写回，结构化需求、评分规则和版本号已更新。');
  };
  const updateStatus = async (id: string, s: string) => runAction(async () => poster(`/proposals/${id}/status`, { proposal_status: s }), `方案状态已更新为${statusLabel(s)}。`);
  const removeProposal = async (id: string, name: string) => {
    if (!window.confirm(`确认删除方案项目「${name}」吗？`)) return;
    await runAction(async () => { await deleter(`/proposals/${id}`); setSelectedId(null); setExpanded(false); setEditing(false); }, '方案项目已删除。');
  };
  const open = (title: string, tip: string, text: string) => setModal({ title, tip, text });

  return <div className="page-stack"><PageHeader title="招投标 / 方案生成智能体" description="围绕招标文件解析、方案编制、知识召回、风险审校与版本管理，打造更完整的投标与方案工作台。" />{message ? <AlertBanner title="执行成功" message={message} tone="success" /> : null}{error ? <AlertBanner title="执行失败" message={error} tone="danger" /> : null}<section className="hero-panel"><div className="hero-panel__main"><div className="hero-panel__eyebrow">方案智能分析</div><h3>将项目洞察、方案状态、风险等级与智能生成流程统一在同一个视图中</h3><p>面向方案经理、售前顾问和投标团队，统一管理项目优先级、审批状态、招标文件结构化结果和技术商务方案的生成过程，提升输出质量与交付效率。</p><div className="hero-panel__meta"><span>支持招标文件解析</span><span>知识与案例召回</span><span>技术 / 商务方案协同生成</span></div></div><div className="hero-panel__side"><div className="hero-kpi success"><strong>{projectCount}</strong><span>当前方案项目</span></div><div className="hero-kpi warning"><strong>{highRiskCount}</strong><span>高风险项目</span></div></div></section><section className="stats-grid"><StatCard title="项目总量" value={projectCount} hint="当前方案项目池" /><StatCard title="高风险项目" value={highRiskCount} hint="建议优先复核" tone="warning" /><StatCard title="待审批项目" value={pendingApprovalCount} hint="跨部门协同推进" /><StatCard title="当前选中" value={selected ? String(selected.project_name) : '-'} hint="正在查看的方案项目" /></section><div className="panel"><div className="section-header"><div><h3>新建方案项目</h3><span className="muted-inline">创建后可立即进入智能方案编制与审校流程</span></div></div><ProposalCreateForm onCreated={() => void query.refetch()} /></div><div className={`workspace-grid workspace-grid--proposal ${expanded ? 'is-expanded' : ''}`}><div className="panel workspace-panel workspace-panel--list"><div className="section-header workspace-header"><div><h3>项目列表</h3><span className="muted-inline">选择左侧项目后，左右工作区会同步展开，并可一键恢复默认尺寸</span></div><div className="workspace-actions"><StatusBadge value={query.data?.length ?? 0} tone="info" /><button className="ghost-btn" type="button" onClick={() => setExpanded(false)} disabled={!expanded}>恢复默认尺寸</button></div></div><div className="list-table scroll-area workspace-scroll workspace-scroll--list">{(query.data ?? []).map((i) => <button className={`list-button ${selected && String(selected.id) === String(i.id) ? 'is-selected' : ''}`} key={String(i.id)} onClick={() => { setSelectedId(String(i.id)); setExpanded(true); setEditing(false); }}><div className={`list-row dense ${selected && String(selected.id) === String(i.id) ? 'is-selected' : ''}`}><strong>{String(i.project_name)}</strong><span><StatusBadge value={String(i.proposal_status)} /></span><span><StatusBadge value={String(i.approval_status)} /></span><span><StatusBadge value={String(i.risk_level)} /></span><span>{bidTypeLabel(String(i.bid_type))}</span></div></button>)}</div></div><div className="panel workspace-panel workspace-panel--detail"><div className="section-header workspace-header"><div><h3>方案详情</h3><span className="muted-inline">后三块内容不会自动出现，需要在下方运行一次智能方案生成后才会写回到这里</span></div><div className="workspace-actions">{selected ? <StatusBadge value={expanded ? '已联动' : '默认视图'} tone={expanded ? 'success' : 'neutral'} /> : null}<button className="ghost-btn" type="button" onClick={() => setExpanded(false)} disabled={!expanded}>收起到默认视图</button></div></div>{selected ? <div className="page-stack scroll-area workspace-scroll workspace-scroll--detail"><div className="action-row"><button className="ghost-btn" type="button" onClick={() => setEditing((p) => !p)}>{editing ? '收起编辑' : '编辑项目'}</button><button className="ghost-btn" type="button" disabled={submitting} onClick={() => void updateStatus(String(selected.id), 'draft')}>回退为草稿</button><button className="ghost-btn" type="button" disabled={submitting} onClick={() => void removeProposal(String(selected.id), String(selected.project_name))}>删除项目</button></div>{editing ? <div className="detail-block"><strong>编辑方案项目</strong><ProposalCreateForm initialProposal={selected} onCreated={() => { setEditing(false); void query.refetch(); }} onCancelled={() => setEditing(false)} /></div> : null}<div className="panel-grid two-columns"><div className="detail-block"><strong>项目画像</strong><div className="detail-grid"><div><strong>项目名称</strong><span>{String(selected.project_name)}</span></div><div><strong>行业编码</strong><span>{String(selected.industry_code)}</span></div><div><strong>方案状态</strong><span><StatusBadge value={String(selected.proposal_status)} /></span></div><div><strong>审批状态</strong><span><StatusBadge value={String(selected.approval_status)} /></span></div><div><strong>风险等级</strong><span><StatusBadge value={String(selected.risk_level)} /></span></div><div><strong>版本号</strong><span>{String(selected.version_no ?? 1)}</span></div></div><div className="action-row"><button className="ghost-btn" disabled={submitting} onClick={() => void updateStatus(String(selected.id), 'rfp_parsed')}>转为已解析</button><button className="ghost-btn" disabled={submitting} onClick={() => void updateStatus(String(selected.id), 'generated')}>转为已生成</button><button className="ghost-btn" disabled={submitting} onClick={() => void updateStatus(String(selected.id), 'reviewing')}>提交评审</button><button className="ghost-btn" disabled={submitting} onClick={() => void updateStatus(String(selected.id), 'approved')}>审批通过</button></div></div><div className="detail-block"><strong>招标文件录入与解析</strong><form className="page-stack" onSubmit={(e) => void submitRfp(e)}><input type="file" accept=".txt,.md,.json,.csv,.html,.htm,.xml,.pdf,.doc,.docx" onChange={(e) => setRfpFile(e.target.files?.[0] ?? null)} /><textarea value={rfpContent} onChange={(e) => setRfpContent(e.target.value)} placeholder="可选：补充粘贴招标文件内容，系统会与上传文件合并解析" rows={6} /><div className="muted-inline">支持本地导入 txt / md / json / csv / html / xml / pdf / doc / docx 等格式。</div><div className="action-row"><button className="primary-btn" type="submit" disabled={submitting}>{submitting ? '解析中...' : '上传文件并解析'}</button></div></form></div></div><DetailCard title="招标文件解析区" tip="支持卡片滚动预览与中央弹窗展开阅读。" text={requirement} onOpen={() => open('招标文件解析区', '查看完整结构化需求与投标关注重点。', requirement)} /><DetailCard title="评分规则" tip="补充评分结构、评审建议和备注说明。" text={scoring} onOpen={() => open('评分规则', '查看完整评分结构、建议与备注。', scoring)} /><DetailCard title="技术方案草稿" tip={technicalReady ? '已生成内容，可滚动预览并展开阅读全文。' : proposalStatus === 'generated' ? '当前状态已是“已生成”，但该板块还没有写回结果，建议重新执行一次下方智能方案生成。' : '该板块尚未生成，需在下方运行一次智能方案生成后才会写回。'} badge={technicalReady ? { value: '已生成', tone: 'success' } : proposalStatus === 'generated' ? { value: '待补写回', tone: 'warning' } : { value: '未生成', tone: 'neutral' }} text={technical} onOpen={() => open('技术方案草稿', technicalReady ? '查看技术方案全文与章节建议。' : proposalStatus === 'generated' ? '当前状态已是“已生成”，但技术方案草稿暂未写回，可重新执行一次智能方案生成。' : '当前尚未生成技术方案草稿，请先运行下方智能方案生成。', technical)} /><DetailCard title="商务方案草稿" tip={commercialReady ? '已生成内容，可滚动预览并展开阅读全文。' : proposalStatus === 'generated' ? '当前状态已是“已生成”，但该板块还没有写回结果，建议重新执行一次下方智能方案生成。' : '该板块尚未生成，需在下方运行一次智能方案生成后才会写回。'} badge={commercialReady ? { value: '已生成', tone: 'success' } : proposalStatus === 'generated' ? { value: '待补写回', tone: 'warning' } : { value: '未生成', tone: 'neutral' }} text={commercial} onOpen={() => open('商务方案草稿', commercialReady ? '查看商务方案全文与风险条款建议。' : proposalStatus === 'generated' ? '当前状态已是“已生成”，但商务方案草稿暂未写回，可重新执行一次智能方案生成。' : '当前尚未生成商务方案草稿，请先运行下方智能方案生成。', commercial)} /><DetailCard title="方案大纲" tip={outlineReady ? '已生成内容，可滚动预览并展开阅读全文。' : proposalStatus === 'generated' ? '当前状态已是“已生成”，但该板块还没有写回结果，建议重新执行一次下方智能方案生成。' : '该板块尚未生成，需在下方运行一次智能方案生成后才会写回。'} badge={outlineReady ? { value: '已生成', tone: 'success' } : proposalStatus === 'generated' ? { value: '待补写回', tone: 'warning' } : { value: '未生成', tone: 'neutral' }} text={outline} onOpen={() => open('方案大纲', outlineReady ? '查看完整方案目录、章节结构与编排建议。' : proposalStatus === 'generated' ? '当前状态已是“已生成”，但方案大纲暂未写回，可重新执行一次智能方案生成。' : '当前尚未生成方案大纲，请先运行下方智能方案生成。', outline)} /></div> : <div className="empty-state workspace-empty-state"><strong>请选择一个方案项目</strong><span>从左侧选择项目后，可查看结构化需求、评分办法与方案生成上下文，并自动展开联动工作区。</span></div>}</div></div><AIActionPanel title="智能方案生成助手" scene="proposal_generation" entityId={selected ? String(selected.id) : undefined} context={{ project_name: selected?.project_name, industry_code: selected?.industry_code, bid_type: selected?.bid_type, risk_level: selected?.risk_level, proposal_status: selected?.proposal_status, approval_status: selected?.approval_status, version_no: selected?.version_no, owner_user_id: selected?.owner_user_id, requirement_json: selected?.requirement_json, scoring_rule_json: selected?.scoring_rule_json, generated_outline_uri: selected?.generated_outline_uri, technical_draft_uri: selected?.technical_draft_uri, commercial_draft_uri: selected?.commercial_draft_uri }} onExecuted={() => void query.refetch()} />{modal ? <DetailModal title={modal.title} tip={modal.tip} text={modal.text} onClose={() => setModal(null)} /> : null}</div>;
}
