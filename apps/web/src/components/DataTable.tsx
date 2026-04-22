type Column<T> = {
  key: keyof T;
  title: string;
};

export function DataTable<T extends Record<string, unknown>>(props: {
  columns: Column<T>[];
  data: T[];
}) {
  return (
    <div className="table-shell">
      <div className="table-header">
        {props.columns.map((column) => (
          <strong key={String(column.key)}>{column.title}</strong>
        ))}
      </div>
      {props.data.map((row, rowIndex) => (
        <div className="table-row" key={rowIndex}>
          {props.columns.map((column) => (
            <span key={String(column.key)}>{String(row[column.key] ?? '')}</span>
          ))}
        </div>
      ))}
    </div>
  );
}
