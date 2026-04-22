export function AlertBanner(props: {
  title: string;
  message: string;
  tone?: 'info' | 'warning' | 'danger' | 'success';
}) {
  return (
    <div className={`alert-banner ${props.tone ?? 'info'}`}>
      <strong>{props.title}</strong>
      <span>{props.message}</span>
    </div>
  );
}
