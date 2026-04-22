export function PageHeader(props: { title: string; description: string }) {
  return (
    <div className="page-header">
      <div className="page-header__main">
        <div className="page-header__eyebrow">工作台</div>
        <h2>{props.title}</h2>
        <p>{props.description}</p>
      </div>
      <div className="page-actions">
        <button className="ghost-btn" type="button">导出视图</button>
        <button className="primary-btn" type="button">新建任务</button>
      </div>
    </div>
  );
}
