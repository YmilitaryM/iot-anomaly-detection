import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import DataTable from '../components/DataTable'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'
import { fetchDevices, type Device } from '../api'
import { usePolling } from '../hooks/usePolling'

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([])
  const [search, setSearch] = useState('')

  const navigate = useNavigate()

  const loadDevices = () => {
    fetchDevices().then(r => setDevices(r.items))
  }

  useEffect(() => { loadDevices() }, [])
  usePolling(loadDevices, 5000)

  const filtered = devices.filter(d => {
    if (search && !d.device_id.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const columns = [
    { key: 'device_id', label: 'Device', flex: 2, render: (r: Record<string, unknown>) => (
      <span style={{ fontWeight: 500 }}>{String(r.device_id)}</span>
    )},
    { key: 'device_type', label: 'Type', flex: 1 },
    { key: 'sensors', label: 'Sensors', flex: 0.8, render: () => <span style={{ color: '#94a3b8' }}>4</span> },
    { key: 'status', label: 'Status', flex: 1, render: (r: Record<string, unknown>) => {
      const status = String(r.training_status || 'active')
      return <StatusBadge variant={status === 'active' ? 'healthy' : 'warning'} label={status} />
    }},
    { key: 'training_status', label: 'Training', flex: 1, render: (r: Record<string, unknown>) => (
      <span style={{ color: '#94a3b8' }}>{String(r.training_status || 'active')}</span>
    )},
    { key: 'arrow', label: '', flex: 0.3, render: () => <span style={{ color: '#64748b' }}>→</span> },
  ]

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12, alignItems: 'center' }}>
        <div className="search-bar">
          <span style={{ color: '#475569' }}>🔍</span>
          <input
            placeholder="Search devices..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon="📡" message={search ? 'No devices match your search' : 'No devices registered yet — ingest data via API'} />
      ) : (
        <DataTable
          columns={columns}
          rows={filtered.map(d => ({ ...d } as unknown as Record<string, unknown>))}
          onRowClick={row => navigate(`/devices/${row.device_id}`)}
          rowKey={r => String(r.device_id)}
        />
      )}
    </div>
  )
}
