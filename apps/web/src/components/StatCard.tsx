export function StatCard(props: {
  title: string;
  value: string | number;
  hint?: string;
  tone?: 'default' | 'warning' | 'danger' | 'success';
}) {
  return (
    <div className={`stat-card ${props.tone ?? 'default'}`}>
      <span className="stat-title">{props.title}</span>
      <strong className="stat-value">{props.value}</strong>
      {props.hint ? <span className="stat-hint">{props.hint}</span> : null}
      <div className="muted-inline">实时更新</div>
    </div>
  );
}
