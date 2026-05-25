import type { ReactNode } from 'react'

export interface Column<T> {
  key: string
  label: string
  flex: number
  render?: (row: T) => ReactNode
}

interface DataTableProps<T> {
  columns: Column<T>[]
  rows: T[]
  onRowClick?: (row: T) => void
  rowKey: (row: T) => string
}

export default function DataTable<T>({ columns, rows, onRowClick, rowKey }: DataTableProps<T>) {
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
              {col.render ? col.render(row) : String((row as Record<string, unknown>)[col.key] ?? '')}
            </span>
          ))}
        </div>
      ))}
    </div>
  )
}
