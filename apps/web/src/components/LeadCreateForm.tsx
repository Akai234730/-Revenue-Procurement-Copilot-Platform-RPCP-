import { useEffect, useState } from 'react';

import { APIError, poster, putter } from '../lib/api';
import type { LeadRecord } from '../types';
import { AlertBanner } from './AlertBanner';

export function LeadCreateForm(props: { onCreated?: () => void; initialLead?: LeadRecord | null; onCancelled?: () => void }) {
  const [companyName, setCompanyName] = useState('');
  const [contactName, setContactName] = useState('');
  const [contactTitle, setContactTitle] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [industryName, setIndustryName] = useState('');
  const [regionCode, setRegionCode] = useState('');
  const [companySize, setCompanySize] = useState('');
  const [demandSummary, setDemandSummary] = useState('');
  const [projectStage, setProjectStage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const isEditMode = Boolean(props.initialLead?.id);

  useEffect(() => {
    const lead = props.initialLead;
    setCompanyName(lead?.company_name ?? '');
    setContactName(lead?.contact_name ?? '');
    setContactTitle(lead?.contact_title ?? '');
    setPhone(lead?.phone ?? '');
    setEmail(lead?.email ?? '');
    setIndustryName(lead?.industry_name ?? '');
    setRegionCode(lead?.region_code ?? '');
    setCompanySize(lead?.company_size ?? '');
    setDemandSummary(lead?.demand_summary ?? '');
    setProjectStage(lead?.project_stage ?? '');
    setMessage('');
    setError('');
  }, [props.initialLead]);

  const resetForm = () => {
    setCompanyName('');
    setContactName('');
    setContactTitle('');
    setPhone('');
    setEmail('');
    setIndustryName('');
    setRegionCode('');
    setCompanySize('');
    setDemandSummary('');
    setProjectStage('');
  };

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setMessage('');
    setError('');
    try {
      const payload = {
        company_name: companyName,
        contact_name: contactName,
        contact_title: contactTitle,
        phone,
        email: email || null,
        industry_name: industryName,
        region_code: regionCode,
        company_size: companySize,
        demand_summary: demandSummary,
        project_stage: projectStage,
        source_channel: 'manual',
      };

      if (isEditMode && props.initialLead?.id) {
        await putter(`/leads/${props.initialLead.id}`, payload);
        setMessage('线索信息已更新，可继续调整状态与跟进动作。');
      } else {
        await poster('/leads', payload);
        resetForm();
        setMessage('线索已创建，可继续补充智能分析与跟进动作。');
      }
      props.onCreated?.();
    } catch (submitError) {
      if (submitError instanceof APIError) {
        setError(`${submitError.code}: ${submitError.message}`);
      } else {
        setError(isEditMode ? '线索更新失败，请稍后重试。' : '线索创建失败，请稍后重试。');
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
        <input value={companyName} onChange={(e) => setCompanyName(e.target.value)} placeholder="客户名称" required />
        <input value={contactName} onChange={(e) => setContactName(e.target.value)} placeholder="联系人" required />
        <input value={contactTitle} onChange={(e) => setContactTitle(e.target.value)} placeholder="联系人职位" />
        <input value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="联系电话" />
      </div>
      <div className="form-grid">
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="邮箱" type="email" />
        <input value={industryName} onChange={(e) => setIndustryName(e.target.value)} placeholder="行业名称" />
        <input value={regionCode} onChange={(e) => setRegionCode(e.target.value)} placeholder="地区编码" />
        <input value={companySize} onChange={(e) => setCompanySize(e.target.value)} placeholder="企业规模" />
      </div>
      <div className="form-grid two-columns">
        <input value={projectStage} onChange={(e) => setProjectStage(e.target.value)} placeholder="项目阶段" />
        <input value={demandSummary} onChange={(e) => setDemandSummary(e.target.value)} placeholder="需求摘要" />
      </div>
      <div className="action-row">
        <button className="primary-btn" type="submit" disabled={submitting}>{submitting ? (isEditMode ? '保存中...' : '创建中...') : (isEditMode ? '保存线索' : '创建线索')}</button>
        {isEditMode ? <button className="ghost-btn" type="button" onClick={props.onCancelled}>取消编辑</button> : null}
      </div>
    </form>
  );
}
