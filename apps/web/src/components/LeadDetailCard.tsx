import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';

import { APIError, deleter, fetcher, poster } from '../lib/api';
import type { LeadRecord } from '../types';
import { AlertBanner } from './AlertBanner';
import { LeadCreateForm } from './LeadCreateForm';
import { LeadFollowupForm } from './LeadFollowupForm';
import { StatusBadge } from './StatusBadge';

type LeadDetail = LeadRecord & {
  followups?: Array<Record<string, unknown>>;
};

function getLeadStatusLabel(status: string): string {
  const labels: Record<string, string> = {
    new: '新建',
    contacted: '已联系',
    qualified: '已确认',
    proposal: '方案阶段',
    won: '已赢单',
    lost: '已丢单',
    archived: '已归档',
    invalid: '无效',
  };

  return labels[status] ?? status;
}

function getFollowupTypeLabel(value: string): string {
  const labels: Record<string, string> = {
    call: '电话跟进',
    visit: '拜访跟进',
    wechat: '微信跟进',
    email: '邮件跟进',
    system: '系统记录',
    ai_analysis: '智能分析',
  };
  return labels[value] ?? value;
}

function getFollowupResultLabel(value: string): string {
  return getLeadStatusLabel(value);
}

function getFollowupPreview(value: unknown): string {
  const content = String(value ?? '').replace(/\s+/g, ' ').trim();
  if (content.length <= 72) return content || '-';
  return `${content.slice(0, 72)}...`;
}

export function LeadDetailCard(props: { lead?: LeadRecord | null; onChanged?: () => void; expanded?: boolean; onResetLayout?: () => void }) {
  const detailQuery = useQuery({
    queryKey: ['lead-detail', props.lead?.id],
    queryFn: () => fetcher<LeadDetail>(`/leads/${props.lead?.id}`),
    enabled: Boolean(props.lead?.id),
  });
  const [statusSubmitting, setStatusSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [statusError, setStatusError] = useState('');
  const [invalidReason, setInvalidReason] = useState('');
  const [editing, setEditing] = useState(false);
  const [followupDraftContent, setFollowupDraftContent] = useState('');
  const [followupDraftResult, setFollowupDraftResult] = useState('');
  const [crmSubmitting, setCrmSubmitting] = useState(false);
  const [expandedFollowup, setExpandedFollowup] = useState<Record<string, unknown> | null>(null);

  if (!props.lead) {
    return (
      <div className="panel workspace-panel workspace-panel--detail page-stack">
        <div className="section-header workspace-header">
          <div>
            <h3>线索详情</h3>
            <span className="muted-inline">线索画像</span>
          </div>
        </div>
        <div className="empty-state workspace-empty-state">
          <strong>请选择左侧线索</strong>
          <span>查看客户画像、风险信号、推荐动作与跟进建议，形成更完整的销售推进视图。</span>
        </div>
      </div>
    );
  }

  const detail = detailQuery.data ?? props.lead;

  const refreshAll = async () => {
    await detailQuery.refetch();
    props.onChanged?.();
  };

  const changeStatus = async (leadStatus: string, reason?: string) => {
    setStatusSubmitting(true);
    setStatusMessage('');
    setStatusError('');
    try {
      await poster(`/leads/${detail.id}/status`, {
        lead_status: leadStatus,
        invalid_reason: reason ?? '',
      });
      setStatusMessage(`线索状态已更新为${getLeadStatusLabel(leadStatus)}。`);
      if (leadStatus === 'invalid') {
        setInvalidReason('');
      }
      await refreshAll();
    } catch (submitError) {
      if (submitError instanceof APIError) {
        setStatusError(`${submitError.code}: ${submitError.message}`);
      } else {
        setStatusError('线索状态更新失败，请稍后重试。');
      }
    } finally {
      setStatusSubmitting(false);
    }
  };

  const removeLead = async () => {
    if (!window.confirm(`确认删除线索「${detail.company_name}」吗？删除后跟进记录也会一并删除。`)) return;
    setStatusSubmitting(true);
    setStatusMessage('');
    setStatusError('');
    try {
      await deleter(`/leads/${detail.id}`);
      setStatusMessage('线索已删除。');
      props.onChanged?.();
    } catch (submitError) {
      if (submitError instanceof APIError) {
        setStatusError(`${submitError.code}: ${submitError.message}`);
      } else {
        setStatusError('线索删除失败，请稍后重试。');
      }
    } finally {
      setStatusSubmitting(false);
    }
  };

  const markInvalid = async () => {
    if (!invalidReason.trim()) {
      setStatusError('请先填写无效原因。');
      return;
    }
    await changeStatus('invalid', invalidReason.trim());
  };

  const generateFollowupDraft = () => {
    setStatusMessage('');
    setStatusError('');
    const draft = [
      `您好，我是负责 ${detail.company_name} 项目的顾问。`,
      `结合贵司当前所处的${getLeadStatusLabel(detail.lead_status)}阶段，以及${detail.industry_name || '当前行业'}的推进情况，我们建议优先围绕“${detail.ai_next_action || '下一步合作重点'}”展开沟通。`,
      `从当前评分 ${detail.ai_lead_score} 分和优先级 ${detail.ai_priority_level} 来看，这条线索值得尽快安排一次电话或线上交流，进一步确认预算、时间计划和关键决策人。`,
      '如果方便，本周我们可先做一次简短沟通，再根据交流结果准备更有针对性的方案材料。',
    ].join('');
    setFollowupDraftContent(draft);
    setFollowupDraftResult(getLeadStatusLabel(detail.lead_status));
    setStatusMessage('已生成一版跟进话术草稿，你可以在下方“新增跟进”中继续编辑后提交。');
  };

  const syncToCrm = async () => {
    setCrmSubmitting(true);
    setStatusMessage('');
    setStatusError('');
    try {
      await poster(`/leads/${detail.id}/sync-crm`, {});
      setStatusMessage('已成功写入客户管理系统，同步状态已更新。');
      await refreshAll();
    } catch (submitError) {
      if (submitError instanceof APIError) {
        setStatusError(`${submitError.code}: ${submitError.message}`);
      } else {
        setStatusError('写入客户管理系统失败，请稍后重试。');
      }
    } finally {
      setCrmSubmitting(false);
    }
  };

  return (
    <div className="panel workspace-panel workspace-panel--detail page-stack">
      <div className="section-header workspace-header">
        <div>
          <h3>线索详情</h3>
          <span className="muted-inline">展开时会与左侧列表同步放大，便于连续切换查看</span>
        </div>
        <div className="workspace-actions">
          <StatusBadge value={props.expanded ? '已联动' : '默认视图'} tone={props.expanded ? 'success' : 'neutral'} />
          <button className="ghost-btn" type="button" onClick={props.onResetLayout} disabled={!props.expanded}>
            收起到默认视图
          </button>
        </div>
      </div>

      <div className="scroll-area workspace-scroll workspace-scroll--detail">
        <div className="page-stack">
          {statusMessage ? <AlertBanner title="操作成功" message={statusMessage} tone="success" /> : null}
          {statusError ? <AlertBanner title="操作失败" message={statusError} tone="danger" /> : null}

          <div className="action-row">
            <button className="ghost-btn" type="button" onClick={() => setEditing((prev) => !prev)}>
              {editing ? '收起编辑' : '编辑线索'}
            </button>
            <button className="ghost-btn" type="button" disabled={statusSubmitting} onClick={() => void changeStatus('new')}>
              回退为新建
            </button>
            <button className="ghost-btn" type="button" disabled={statusSubmitting} onClick={() => void removeLead()}>
              删除线索
            </button>
          </div>

          {editing ? <div className="detail-block"><strong>编辑线索</strong><LeadCreateForm initialLead={detail} onCreated={() => { setEditing(false); void refreshAll(); }} onCancelled={() => setEditing(false)} /></div> : null}

          <div className="panel-grid two-columns">
            <div className="detail-block">
              <strong>客户画像</strong>
              <div className="detail-grid">
                <div><strong>客户名称</strong><span>{detail.company_name}</span></div>
                <div><strong>联系人</strong><span>{detail.contact_name}</span></div>
                <div><strong>行业</strong><span>{detail.industry_name}</span></div>
                <div><strong>来源</strong><span>{detail.source_channel}</span></div>
                <div><strong>优先级</strong><span><StatusBadge value={detail.ai_priority_level} /></span></div>
                <div><strong>成熟度</strong><span><StatusBadge value={detail.ai_maturity_level} /></span></div>
                <div><strong>客户管理同步</strong><span><StatusBadge value={detail.crm_sync_status} /></span></div>
                <div><strong>线索状态</strong><span><StatusBadge value={detail.lead_status} /></span></div>
                <div><strong>无效原因</strong><span>{detail.invalid_reason || '-'}</span></div>
                <div><strong>智能评分</strong><span>{detail.ai_lead_score}</span></div>
              </div>
            </div>

            <div className="detail-block">
              <strong>销售判断</strong>
              <div className="signal-list">
                <div className="signal-item">
                  <strong>智能推荐动作</strong>
                  <span>{detail.ai_next_action}</span>
                </div>
                <div className="signal-item">
                  <strong>推进重点</strong>
                  <span>优先围绕客户当前成熟度和优先级制定跟进节奏，避免高价值线索迟迟没有进入下一步。</span>
                </div>
                <div className="signal-item">
                  <strong>协同建议</strong>
                  <span>必要时联动售前与方案团队补充客户需求理解、方案材料和内部资源协调。</span>
                </div>
              </div>
            </div>
          </div>

          <div className="detail-block">
            <strong>状态流转</strong>
            <div className="action-row">
              <button className="ghost-btn" type="button" disabled={statusSubmitting} onClick={() => void changeStatus('new')}>转为新建</button>
              <button className="ghost-btn" type="button" disabled={statusSubmitting} onClick={() => void changeStatus('contacted')}>转为已联系</button>
              <button className="ghost-btn" type="button" disabled={statusSubmitting} onClick={() => void changeStatus('qualified')}>转为已确认</button>
              <button className="ghost-btn" type="button" disabled={statusSubmitting} onClick={() => void changeStatus('proposal')}>转为方案阶段</button>
              <button className="ghost-btn" type="button" disabled={statusSubmitting} onClick={() => void changeStatus('won')}>转为已赢单</button>
              <button className="ghost-btn" type="button" disabled={statusSubmitting} onClick={() => void changeStatus('lost')}>转为已丢单</button>
              <button className="ghost-btn" type="button" disabled={statusSubmitting} onClick={() => void changeStatus('archived')}>转为已归档</button>
            </div>
            <div className="form-grid compact">
              <input
                value={invalidReason}
                onChange={(event) => setInvalidReason(event.target.value)}
                placeholder="填写无效原因后可标记为无效"
              />
              <button className="ghost-btn" type="button" disabled={statusSubmitting} onClick={() => void markInvalid()}>
                转为无效
              </button>
            </div>
          </div>

          <div className="detail-block">
            <strong>新增跟进</strong>
            <LeadFollowupForm leadId={detail.id} draftContent={followupDraftContent} draftResult={followupDraftResult} onCreated={() => { setFollowupDraftContent(''); setFollowupDraftResult(''); void refreshAll(); }} />
          </div>

          <div className="detail-block detail-block--scroll">
            <strong>跟进记录</strong>
            <div className="list-table scroll-area scroll-area--md">
              {(detail.followups ?? []).map((item, index) => (
                <div className="list-row followup-row" key={index}>
                  <div className="followup-row__main">
                    <div className="followup-row__meta">
                      <strong>{getFollowupTypeLabel(String(item.followup_type))}</strong>
                      <span>{getFollowupResultLabel(String(item.followup_result))}</span>
                    </div>
                    <p className="followup-row__preview">{getFollowupPreview(item.followup_content)}</p>
                  </div>
                  <button className="ghost-btn" type="button" onClick={() => setExpandedFollowup(item)}>查看全文</button>
                </div>
              ))}
            </div>
          </div>

          {expandedFollowup ? (
            <div className="proposal-modal-backdrop" onClick={() => setExpandedFollowup(null)}>
              <div
                className="proposal-modal"
                role="dialog"
                aria-modal="true"
                aria-label="跟进记录全文查看"
                onClick={(event) => event.stopPropagation()}
              >
                <div className="proposal-modal__header">
                  <div>
                    <div className="hero-panel__eyebrow">跟进记录全文</div>
                    <h3>{getFollowupTypeLabel(String(expandedFollowup.followup_type))}</h3>
                    <p>可完整查看这条历史跟进的结果与内容。</p>
                  </div>
                  <button className="ghost-btn" type="button" onClick={() => setExpandedFollowup(null)}>
                    关闭
                  </button>
                </div>
                <div className="proposal-modal__content scroll-area">
                  <div className="page-stack">
                    <div className="detail-block">
                      <strong>跟进结果</strong>
                      <span>{getFollowupResultLabel(String(expandedFollowup.followup_result))}</span>
                    </div>
                    <div className="detail-block">
                      <strong>跟进内容</strong>
                      <p>{String(expandedFollowup.followup_content ?? '-')}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          ) : null}

          <div className="action-row">
            <button className="primary-btn" type="button" onClick={generateFollowupDraft}>生成跟进话术</button>
            <button className="ghost-btn" type="button" disabled={crmSubmitting} onClick={() => void syncToCrm()}>{crmSubmitting ? '写入中...' : '写入客户管理系统'}</button>
          </div>
        </div>
      </div>
    </div>
  );
}
