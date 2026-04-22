import { APIError } from '../lib/api';
import { AlertBanner } from './AlertBanner';

export function QueryState(props: {
  isLoading: boolean;
  error: unknown;
  empty: boolean;
  emptyTitle: string;
  emptyMessage: string;
}) {
  if (props.isLoading) {
    return <div className="empty-state"><strong>正在加载</strong><span>系统正在同步最新数据与视图状态，请稍候。</span></div>;
  }

  if (props.error) {
    const message = props.error instanceof APIError ? `${props.error.code}: ${props.error.message}` : '加载失败，请稍后重试。';
    return <AlertBanner title="数据加载异常" message={message} tone="danger" />;
  }

  if (props.empty) {
    return (
      <div className="empty-state">
        <strong>{props.emptyTitle}</strong>
        <span>{props.emptyMessage}</span>
      </div>
    );
  }

  return null;
}
