import type { ReactNode } from 'react'

interface Column {
  key: string
  label: string
  flex: number
  render?: (row: Record<string, unknown>) => ReactNode
}

interface DataTableProps {
  columns: Column[]
  rows: Record<string, unknown>[]
  onRowClick?: (row: Record<string, unknown>) => void
  rowKey: (row: Record<string, unknown>) => string
}

export default function DataTable({ columns, rows, onRowClick, rowKey }: DataTableProps) {
  return (
    <div className="data-table">
      <div className="data-table-header">
        {columns.map(col => (
          <span key={col.key} style={{ flex: col.flex }}>{col.label}</span>
        ))}
      </div>
      {rows.map(row => (
        <div
          key={rowKey(row)}
          className="data-table-row"
          onClick={() => onRowClick?.(row)}
        >
          {columns.map(col => (
            <span key={col.key} style={{ flex: col.flex }}>
              {col.render ? col.render(row) : String(row[col.key] ?? '')}
            </span>
          ))}
        </div>
      ))}
    </div>
  )
}
