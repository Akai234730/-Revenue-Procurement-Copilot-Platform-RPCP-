export function EmptyState(props: { title: string; message: string }) {
  return (
    <div className="empty-state system-empty-state">
      <div className="system-empty-state__badge">待处理</div>
      <strong>{props.title}</strong>
      <span>{props.message}</span>
    </div>
  );
}
