import { useEffect, useState } from 'react';

import { APIError, poster, putter } from '../lib/api';
import { AlertBanner } from './AlertBanner';

export function ProposalCreateForm(props: {
  onCreated?: () => void;
  initialProposal?: Record<string, unknown> | null;
  onCancelled?: () => void;
}) {
  const [projectName, setProjectName] = useState('');
  const [customerId, setCustomerId] = useState('');
  const [industryCode, setIndustryCode] = useState('');
  const [bidType, setBidType] = useState('rfp');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const isEditMode = Boolean(props.initialProposal?.id);

  useEffect(() => {
    setProjectName(String(props.initialProposal?.project_name ?? ''));
    setCustomerId(String(props.initialProposal?.customer_id ?? ''));
    setIndustryCode(String(props.initialProposal?.industry_code ?? ''));
    setBidType(String(props.initialProposal?.bid_type ?? 'rfp'));
    setMessage('');
    setError('');
  }, [props.initialProposal]);

  const resetForm = () => {
    setProjectName('');
    setCustomerId('');
    setIndustryCode('');
    setBidType('rfp');
  };

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setMessage('');
    setError('');
    try {
      const payload = {
        project_name: projectName,
        customer_id: customerId,
        industry_code: industryCode,
        bid_type: bidType,
      };

      if (isEditMode && props.initialProposal?.id) {
        await putter(`/proposals/${String(props.initialProposal.id)}`, payload);
        setMessage('方案项目已更新，可继续调整状态与内容。');
      } else {
        await poster('/proposals', payload);
        resetForm();
        setMessage('方案项目已创建，可继续执行招标文件解析与方案生成。');
      }
      props.onCreated?.();
    } catch (submitError) {
      if (submitError instanceof APIError) {
        setError(`${submitError.code}: ${submitError.message}`);
      } else {
        setError(isEditMode ? '方案项目更新失败，请稍后重试。' : '方案项目创建失败，请稍后重试。');
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <form className="page-stack" onSubmit={onSubmit}>
      {message ? <AlertBanner title={isEditMode ? '更新成功' : '创建成功'} message={message} tone="success" /> : null}
      {error ? <AlertBanner title={isEditMode ? '更新失败' : '创建失败'} message={error} tone="danger" /> : null}
      <div className="form-grid">
        <input value={projectName} onChange={(e) => setProjectName(e.target.value)} placeholder="项目名称" required />
        <input value={customerId} onChange={(e) => setCustomerId(e.target.value)} placeholder="客户 ID" />
        <input value={industryCode} onChange={(e) => setIndustryCode(e.target.value)} placeholder="行业编码" />
        <select value={bidType} onChange={(e) => setBidType(e.target.value)}>
          <option value="rfp">招标文件项目</option>
          <option value="tender">招标项目</option>
        </select>
      </div>
      <div className="action-row">
        <button className="primary-btn" type="submit" disabled={submitting}>
          {submitting ? (isEditMode ? '保存中...' : '创建中...') : (isEditMode ? '保存方案项目' : '创建方案项目')}
        </button>
        {isEditMode ? <button className="ghost-btn" type="button" onClick={props.onCancelled}>取消编辑</button> : null}
      </div>
    </form>
  );
}
