import { useEffect, useState } from 'react';

import { APIError, poster } from '../lib/api';
import { AlertBanner } from './AlertBanner';

export function LeadFollowupForm(props: { leadId: string; onCreated?: () => void; draftContent?: string; draftResult?: string }) {
  const [content, setContent] = useState('');
  const [result, setResult] = useState('');
  const [expanded, setExpanded] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    if (props.draftContent !== undefined) setContent(props.draftContent);
  }, [props.draftContent]);

  useEffect(() => {
    if (props.draftResult !== undefined) setResult(props.draftResult);
  }, [props.draftResult]);

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setMessage('');
    setError('');
    try {
      await poster(`/leads/${props.leadId}/followups`, {
        lead_id: props.leadId,
        followup_content: content,
        followup_result: result,
        followup_type: 'call',
        followup_channel: 'phone',
      });
      setContent('');
      setResult('');
      setExpanded(false);
      setMessage('跟进记录已保存。');
      props.onCreated?.();
    } catch (submitError) {
      if (submitError instanceof APIError) {
        setError(`${submitError.code}: ${submitError.message}`);
      } else {
        setError('跟进记录提交失败，请稍后重试。');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <>
      <form className="page-stack" onSubmit={onSubmit}>
        {message ? <AlertBanner title="提交成功" message={message} tone="success" /> : null}
        {error ? <AlertBanner title="提交失败" message={error} tone="danger" /> : null}
        <div className="form-grid compact">
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="跟进内容"
            rows={4}
            required
          />
          <input value={result} onChange={(e) => setResult(e.target.value)} placeholder="跟进结果" required />
        </div>
        <div className="action-row">
          <button className="primary-btn" type="submit" disabled={submitting}>
            {submitting ? '提交中...' : '新增跟进'}
          </button>
          <button className="ghost-btn" type="button" onClick={() => setExpanded(true)} disabled={!content.trim()}>
            展开查看
          </button>
        </div>
      </form>

      {expanded ? (
        <div className="proposal-modal-backdrop" onClick={() => setExpanded(false)}>
          <div
            className="proposal-modal"
            role="dialog"
            aria-modal="true"
            aria-label="跟进内容展开编辑"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="proposal-modal__header">
              <div>
                <div className="hero-panel__eyebrow">新增跟进展开编辑</div>
                <h3>完整查看并编辑跟进内容</h3>
                <p>适合阅读长话术、修改措辞，再决定是否提交为正式跟进记录。</p>
              </div>
              <button className="ghost-btn" type="button" onClick={() => setExpanded(false)}>
                关闭
              </button>
            </div>
            <div className="proposal-modal__content scroll-area">
              <div className="page-stack">
                <textarea value={content} onChange={(e) => setContent(e.target.value)} placeholder="跟进内容" rows={14} />
                <input value={result} onChange={(e) => setResult(e.target.value)} placeholder="跟进结果" />
                <div className="action-row">
                  <button className="primary-btn" type="button" onClick={() => setExpanded(false)}>
                    完成编辑
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </>
  );
}
