import { useEffect, useState } from 'react';

import { APIError, poster, putter } from '../lib/api';
import { AlertBanner } from './AlertBanner';

export function PurchaseRequestCreateForm(props: {
  onCreated?: () => void;
  initialRequest?: Record<string, unknown> | null;
  onCancelled?: () => void;
}) {
  const [demandDesc, setDemandDesc] = useState('');
  const [categoryCode, setCategoryCode] = useState('');
  const [deptId, setDeptId] = useState('');
  const [expectedQuantity, setExpectedQuantity] = useState('1');
  const [budgetAmount, setBudgetAmount] = useState('0');
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const isEditMode = Boolean(props.initialRequest?.id);

  useEffect(() => {
    setDemandDesc(String(props.initialRequest?.demand_desc ?? ''));
    setCategoryCode(String(props.initialRequest?.category_code ?? ''));
    setDeptId(String(props.initialRequest?.dept_id ?? ''));
    setExpectedQuantity(String(props.initialRequest?.expected_quantity ?? '1'));
    setBudgetAmount(String(props.initialRequest?.budget_amount ?? '0'));
    setMessage('');
    setError('');
  }, [props.initialRequest]);

  const resetForm = () => {
    setDemandDesc('');
    setCategoryCode('');
    setDeptId('');
    setExpectedQuantity('1');
    setBudgetAmount('0');
  };

  const onSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setMessage('');
    setError('');
    try {
      const payload = {
        demand_desc: demandDesc,
        category_code: categoryCode,
        dept_id: deptId,
        expected_quantity: Number(expectedQuantity || 0),
        budget_amount: Number(budgetAmount || 0),
      };

      if (isEditMode && props.initialRequest?.id) {
        await putter(`/procurement/purchase-requests/${String(props.initialRequest.id)}`, payload);
        setMessage('采购申请已更新，可继续调整状态与询价流程。');
      } else {
        await poster('/procurement/purchase-requests', payload);
        resetForm();
        setMessage('采购申请已创建，可继续生成询价任务与采购分析。');
      }
      props.onCreated?.();
    } catch (submitError) {
      if (submitError instanceof APIError) {
        setError(`${submitError.code}: ${submitError.message}`);
      } else {
        setError(isEditMode ? '采购申请更新失败，请稍后重试。' : '采购申请创建失败，请稍后重试。');
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
        <input value={demandDesc} onChange={(e) => setDemandDesc(e.target.value)} placeholder="采购需求描述" required />
        <input value={categoryCode} onChange={(e) => setCategoryCode(e.target.value)} placeholder="品类编码" />
        <input value={deptId} onChange={(e) => setDeptId(e.target.value)} placeholder="需求部门 ID" />
        <input value={expectedQuantity} onChange={(e) => setExpectedQuantity(e.target.value)} placeholder="预估数量" type="number" min="1" />
      </div>
      <div className="form-grid two-columns">
        <input value={budgetAmount} onChange={(e) => setBudgetAmount(e.target.value)} placeholder="预算金额" type="number" min="0" step="0.01" />
      </div>
      <div className="action-row">
        <button className="primary-btn" type="submit" disabled={submitting}>{submitting ? (isEditMode ? '保存中...' : '创建中...') : (isEditMode ? '保存采购申请' : '创建采购申请')}</button>
        {isEditMode ? <button className="ghost-btn" type="button" onClick={props.onCancelled}>取消编辑</button> : null}
      </div>
    </form>
  );
}
