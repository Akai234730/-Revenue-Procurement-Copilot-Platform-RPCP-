import { useEffect, useState } from 'react';

import { APIError, poster, putter } from '../lib/api';
import type { SupplierRecord } from '../types';
import { AlertBanner } from './AlertBanner';

export function SupplierCreateForm(props: { onCreated?: () => void; initialSupplier?: SupplierRecord | null; onCancelled?: () => void }) {
  const [supplierName, setSupplierName] = useState('');
  const [supplierCode, setSupplierCode] = useState('');
  const [supplierCategory, setSupplierCategory] = useState('');
  const [qualificationLevel, setQualificationLevel] = useState('');
  const [regionCode, setRegionCode] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const isEditMode = Boolean(props.initialSupplier?.id);

  useEffect(() => {
    const supplier = props.initialSupplier;
    setSupplierName(supplier?.supplier_name ?? '');
    setSupplierCode(supplier?.supplier_code ?? '');
    setSupplierCategory(supplier?.supplier_category ?? '');
    setQualificationLevel(supplier?.qualification_level ?? '');
    setRegionCode(supplier?.region_code ?? '');
    setMessage('');
    setError('');
  }, [props.initialSupplier]);

  const resetForm = () => {
    setSupplierName('');
    setSupplierCode('');
    setSupplierCategory('');
    setQualificationLevel('');
    setRegionCode('');
  };

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setMessage('');
    setError('');
    try {
      const payload = {
        supplier_name: supplierName,
        supplier_code: supplierCode,
        supplier_category: supplierCategory,
        qualification_level: qualificationLevel,
        region_code: regionCode,
      };

      if (isEditMode && props.initialSupplier?.id) {
        await putter(`/suppliers/${props.initialSupplier.id}`, payload);
        setMessage('供应商信息已更新，可继续调整状态与合作策略。');
      } else {
        await poster('/suppliers', payload);
        resetForm();
        setMessage('供应商已创建，可继续查看评估结果与风险分析。');
      }
      props.onCreated?.();
    } catch (submitError) {
      if (submitError instanceof APIError) {
        setError(`${submitError.code}: ${submitError.message}`);
      } else {
        setError(isEditMode ? '供应商更新失败，请稍后重试。' : '供应商创建失败，请稍后重试。');
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
        <input value={supplierName} onChange={(e) => setSupplierName(e.target.value)} placeholder="供应商名称" required />
        <input value={supplierCode} onChange={(e) => setSupplierCode(e.target.value)} placeholder="供应商编码" />
        <input value={supplierCategory} onChange={(e) => setSupplierCategory(e.target.value)} placeholder="供应商分类" />
        <input value={qualificationLevel} onChange={(e) => setQualificationLevel(e.target.value)} placeholder="资质等级" />
      </div>
      <div className="form-grid two-columns">
        <input value={regionCode} onChange={(e) => setRegionCode(e.target.value)} placeholder="地区编码" />
      </div>
      <div className="action-row">
        <button className="primary-btn" type="submit" disabled={submitting}>{submitting ? (isEditMode ? '保存中...' : '创建中...') : (isEditMode ? '保存供应商' : '创建供应商')}</button>
        {isEditMode ? <button className="ghost-btn" type="button" onClick={props.onCancelled}>取消编辑</button> : null}
      </div>
    </form>
  );
}
