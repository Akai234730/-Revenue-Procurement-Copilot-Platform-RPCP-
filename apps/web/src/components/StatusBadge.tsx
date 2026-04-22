type StatusTone = 'neutral' | 'info' | 'success' | 'warning' | 'danger';

function inferTone(value: string): StatusTone {
  const normalized = value.toLowerCase();
  if (['high', 'danger', 'failed', 'error', 'rejected', 'blocked', 'overdue', 'cancelled', 'lost', 'invalid'].some((item) => normalized.includes(item))) {
    return 'danger';
  }
  if (['warning', 'pending', 'queued', 'review', 'draft', 'medium', 'rfp_parsed', 'quoted', 'sourcing', 'proposal'].some((item) => normalized.includes(item))) {
    return 'warning';
  }
  if (['approved', 'completed', 'success', 'active', 'connected', 'done', 'low', 'generated', 'awarded', 'qualified', 'synced'].some((item) => normalized.includes(item))) {
    return 'success';
  }
  if (['running', 'processing', 'open', 'new', 'published', 'contacted', 'vectorized'].some((item) => normalized.includes(item))) {
    return 'info';
  }
  return 'neutral';
}

function formatLabel(value: string | number | null | undefined): string {
  if (value === null || value === undefined) return '-';
  if (typeof value === 'number') return String(value);

  const normalized = value.toLowerCase();
  const labels: Record<string, string> = {
    high: '高',
    medium: '中',
    low: '低',
    pending: '待处理',
    queued: '排队中',
    draft: '草稿',
    reviewing: '评审中',
    review: '评审中',
    approved: '已通过',
    rejected: '已拒绝',
    generated: '已生成',
    rfp_parsed: '已解析',
    published: '已发布',
    quoted: '已报价',
    awarded: '已定标',
    sourcing: '寻源中',
    proposal: '方案阶段',
    contacted: '已联系',
    qualified: '已确认',
    won: '已赢单',
    lost: '已丢单',
    archived: '已归档',
    invalid: '无效',
    active: '启用',
    connected: '已连接',
    synced: '已同步',
    success: '成功',
    completed: '已完成',
    done: '已完成',
    running: '运行中',
    processing: '处理中',
    open: '开启',
    new: '新建',
    failed: '失败',
    error: '异常',
    cancelled: '已取消',
    blocked: '已阻塞',
    overdue: '已逾期',
    warning: '预警',
    danger: '高风险',
    vectorized: '已向量化',
  };

  return labels[normalized] ?? value;
}

export function StatusBadge(props: { value: string | number | null | undefined; tone?: StatusTone }) {
  const rawLabel = String(props.value ?? '-');
  const tone = props.tone ?? inferTone(rawLabel);
  const label = formatLabel(props.value);
  return <span className={`status-badge ${tone}`}>{label}</span>;
}
