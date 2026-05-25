import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DataTable from '../components/DataTable'
import FilterTabs from '../components/FilterTabs'
import SeverityDot from '../components/SeverityDot'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'
import type { AlertEvent } from '../api'

interface AlertsPageProps {
  alerts: AlertEvent[]
}

export default function AlertsPage({ alerts }: AlertsPageProps) {
  const [severityFilter, setSeverityFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('all')
  const navigate = useNavigate()

  const filtered = alerts.filter(a => {
    if (severityFilter !== 'all' && a.severity !== severityFilter) return false
    if (statusFilter !== 'all' && a.status !== statusFilter) return false
    return true
  })

  const columns = [
    { key: 'severity', label: '', flex: 0.3, render: (r: Record<string, unknown>) => (
      <SeverityDot severity={String(r.severity) as 'critical' | 'warning' | 'info'} />
    )},
    { key: 'device_id', label: 'Device', flex: 1.2, render: (r: Record<string, unknown>) => (
      <span style={{ fontWeight: 500 }}>{String(r.device_id)}</span>
    )},
    { key: 'sensor_id', label: 'Sensor', flex: 1, render: (r: Record<string, unknown>) => (
      <span style={{ color: '#94a3b8' }}>{String(r.sensor_id)}</span>
    )},
    { key: 'detection_source', label: 'Source', flex: 0.8, render: (r: Record<string, unknown>) => (
      <span style={{ color: '#94a3b8' }}>{String(r.detection_source)}</span>
    )},
    { key: 'anomaly_score', label: 'Score', flex: 0.8, render: (r: Record<string, unknown>) => (
      <span style={{ fontFamily: 'monospace', color: Number(r.anomaly_score) > 0.8 ? '#fca5a5' : '#94a3b8' }}>
        {Number(r.anomaly_score).toFixed(2)}
      </span>
    )},
    { key: 'timestamp', label: 'Time', flex: 1, render: (r: Record<string, unknown>) => {
      const ts = new Date(String(r.timestamp))
      return <span style={{ color: '#64748b' }}>{ts.toLocaleTimeString()}</span>
    }},
    { key: 'status', label: 'Status', flex: 0.6, render: (r: Record<string, unknown>) => (
      <StatusBadge variant={String(r.status) === 'confirmed' ? 'healthy' : String(r.status) === 'rejected' ? 'info' : 'warning'} label={String(r.status)} />
    )},
    { key: 'arrow', label: '', flex: 0.3, render: () => <span style={{ color: '#64748b' }}>→</span> },
  ]

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12, alignItems: 'center' }}>
        <FilterTabs
          options={[
            { key: 'all', label: 'All' },
            { key: 'critical', label: 'Critical' },
            { key: 'warning', label: 'Warning' },
            { key: 'info', label: 'Info' },
          ]}
          selected={severityFilter}
          onChange={setSeverityFilter}
        />
        <FilterTabs
          options={[
            { key: 'all', label: 'All Status' },
            { key: 'open', label: 'Open' },
            { key: 'confirmed', label: 'Confirmed' },
            { key: 'rejected', label: 'Rejected' },
          ]}
          selected={statusFilter}
          onChange={setStatusFilter}
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon="🔔" message="No alerts match your filters" />
      ) : (
        <DataTable
          columns={columns}
          rows={filtered.map(a => ({ ...a } as unknown as Record<string, unknown>))}
          onRowClick={row => navigate(`/alerts/${row.event_id}`)}
          rowKey={r => String(r.event_id)}
        />
      )}
    </div>
  )
}
