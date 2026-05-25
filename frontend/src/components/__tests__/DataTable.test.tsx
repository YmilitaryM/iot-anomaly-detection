import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DataTable from '../DataTable'

const columns = [
  { key: 'name', label: 'Name', flex: 1 },
  { key: 'status', label: 'Status', flex: 1 },
]

const rows = [
  { name: 'pump-001', status: 'OK' },
  { name: 'pump-002', status: 'WARN' },
]

describe('DataTable', () => {
  it('renders header labels', () => {
    render(<DataTable columns={columns} rows={rows} rowKey={r => String(r.name)} />)
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Status')).toBeInTheDocument()
  })

  it('renders row data', () => {
    render(<DataTable columns={columns} rows={rows} rowKey={r => String(r.name)} />)
    expect(screen.getByText('pump-001')).toBeInTheDocument()
    expect(screen.getByText('OK')).toBeInTheDocument()
  })

  it('calls onRowClick when a row is clicked', async () => {
    const onClick = vi.fn()
    render(<DataTable columns={columns} rows={rows} onRowClick={onClick} rowKey={r => String(r.name)} />)
    await userEvent.click(screen.getByText('pump-001'))
    expect(onClick).toHaveBeenCalledWith(rows[0])
  })
})
