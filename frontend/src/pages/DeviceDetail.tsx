import { useParams, useNavigate } from 'react-router-dom'
import { useMemo } from 'react'
import TimeSeriesChart from '../components/TimeSeriesChart'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'
import { useChartData } from '../hooks/useChartData'
import { SENSOR_COLORS } from '../components/TimeSeriesChart'

// Mock sensor list for display
const MOCK_SENSORS = [
  { id: 'temp-01', type: 'temperature', value: 42.3, unit: '°C', color: '#f97316' },
  { id: 'vib-01', type: 'vibration', value: 0.8, unit: 'mm/s', color: '#e11d48' },
  { id: 'cur-01', type: 'current', value: 12.4, unit: 'A', color: '#facc15' },
  { id: 'hum-01', type: 'humidity', value: 72, unit: '%', color: '#22d3ee' },
]

export default function DeviceDetail() {
  const { deviceId } = useParams<{ deviceId: string }>()
  const navigate = useNavigate()
  const { data: chartData } = useChartData(deviceId || '', MOCK_SENSORS[0].id)

  const allSeriesData = useMemo(() => {
    return MOCK_SENSORS.map(s => ({
      name: s.id,
      color: s.color,
      data: chartData.map(d => [d.timestamp, d.value] as [string, number]),
    }))
  }, [chartData])

  if (!deviceId) return <EmptyState message="No device specified" />

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <button
          onClick={() => navigate('/devices')}
          style={{ background: 'none', border: 'none', color: '#64748b', fontSize: 11, cursor: 'pointer' }}
        >
          ← Back to Devices
        </button>
        <span style={{ color: '#334155' }}>|</span>
        <span style={{ color: '#e2e8f0', fontWeight: 600, fontSize: 12 }}>{deviceId}</span>
        <StatusBadge variant="critical" label="Critical Status" />
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        {MOCK_SENSORS.map(s => (
          <div key={s.id} className="sensor-mini-card" style={{ borderTopColor: s.color }}>
            <div className="sensor-mini-card-header">
              <span className="sensor-mini-card-name">{s.id}</span>
              <span className="sensor-mini-card-type">{s.type}</span>
            </div>
            <div className="sensor-mini-card-value">{s.value}{s.unit}</div>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: 12 }}>
        <TimeSeriesChart series={allSeriesData} height={240} title="Sensor Data — All Sensors" />
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <div className="section-card" style={{ flex: 1 }}>
          <div className="section-card-title">Hard Boundary Config</div>
          <div className="config-row">
            {['Min', 'Max', 'Deadband'].map(label => (
              <div className="config-field" key={label}>
                <div className="form-label">{label}</div>
                <input className="form-input" defaultValue={label === 'Deadband' ? '±0.5°C' : label === 'Max' ? '80°C' : '0°C'} />
              </div>
            ))}
            <button className="btn-primary" style={{ alignSelf: 'flex-end' }}>Save</button>
          </div>
        </div>
        <div className="section-card" style={{ flex: 1 }}>
          <div className="section-card-title">Recent Alerts</div>
          <p style={{ fontSize: 10, color: '#94a3b8' }}>CRIT temp-01 85°C <span style={{ color: '#475569', float: 'right' }}>2m ago</span></p>
          <p style={{ fontSize: 10, color: '#94a3b8', marginTop: 4 }}>WARN cur-01 12.4A <span style={{ color: '#475569', float: 'right' }}>12m ago</span></p>
        </div>
      </div>
    </div>
  )
}
