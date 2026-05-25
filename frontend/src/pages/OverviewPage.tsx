import { useState, useMemo } from 'react'
import StatCard from '../components/StatCard'
import TimeSeriesChart from '../components/TimeSeriesChart'
import SeverityDot from '../components/SeverityDot'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'
import { useChartData } from '../hooks/useChartData'
import type { AlertEvent, Device } from '../api'

interface OverviewPageProps {
  alerts: AlertEvent[]
  devices: Device[]
}

export default function OverviewPage({ alerts, devices }: OverviewPageProps) {
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('1h')
  const lookbackMs = { '1h': 3600000, '6h': 21600000, '24h': 86400000, '7d': 604800000 }[timeRange]

  // Pick first device with data as default chart
  const defaultDevice = devices[0]?.device_id || ''
  const defaultSensor = 'temp-01'
  const { data: chartData } = useChartData(defaultDevice, defaultSensor, lookbackMs)

  const criticalCount = alerts.filter(a => a.severity === 'critical').length
  const warningCount = alerts.filter(a => a.severity === 'warning').length
  const healthyCount = devices.length - criticalCount - warningCount

  const seriesData = useMemo(() => {
    return [{
      name: defaultSensor,
      color: '#38bdf8',
      data: chartData.map(d => [d.timestamp, d.value] as [string, number]),
    }]
  }, [chartData])

  const recentAlerts = alerts.slice(0, 5)

  // Generate mock sparkline data from alert counts
  const sparklineMock = [2, 1, 3, 2, 5, 3, 3, 4]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h2 style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 600 }}>Dashboard</h2>
        <div className="time-range-selector">
          {(['1h', '6h', '24h', '7d'] as const).map(r => (
            <button
              key={r}
              className={`time-range-btn ${timeRange === r ? 'active' : ''}`}
              onClick={() => setTimeRange(r)}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <StatCard label="Critical" value={criticalCount} accentColor="#ef4444" sparklineData={sparklineMock} />
        <StatCard label="Warning" value={warningCount} accentColor="#f97316" sparklineData={sparklineMock} />
        <StatCard label="Healthy" value={Math.max(0, healthyCount)} accentColor="#22c55e" />
        <StatCard label="Throughput" value="1.2k" accentColor="#38bdf8" />
      </div>

      <div style={{ marginBottom: 12 }}>
        <TimeSeriesChart series={seriesData} height={260} title="Pump Station A · Temperature" />
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <div className="section-card" style={{ flex: 1 }}>
          <div className="section-card-title">Alert Feed</div>
          {recentAlerts.length === 0 ? (
            <EmptyState message="No alerts yet" />
          ) : (
            recentAlerts.map(a => (
              <div
                key={a.event_id}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  padding: '6px 8px', background: 'var(--color-bg-input)',
                  borderRadius: 3, marginBottom: 4,
                  borderLeft: `2px solid ${a.severity === 'critical' ? 'var(--color-critical)' : a.severity === 'warning' ? 'var(--color-warning)' : 'var(--color-info)'}`,
                }}
              >
                <StatusBadge
                  variant={a.severity === 'critical' ? 'critical' : a.severity === 'warning' ? 'warning' : 'info'}
                  label={a.severity.toUpperCase()}
                />
                <span style={{ fontSize: 10, color: '#e2e8f0' }}>{a.device_id} / {a.sensor_id}</span>
                <span style={{ fontSize: 10, marginLeft: 'auto', color: a.severity === 'critical' ? '#fca5a5' : '#94a3b8' }}>
                  {a.anomaly_score.toFixed(2)}
                </span>
              </div>
            ))
          )}
        </div>

        <div className="section-card" style={{ flex: 1 }}>
          <div className="section-card-title">Device Health</div>
          {devices.length === 0 ? (
            <EmptyState message="No devices registered" />
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                className="donut-chart"
                style={{
                  background: `conic-gradient(#22c55e 0deg ${(healthyCount / Math.max(devices.length, 1)) * 360}deg, #f97316 ${(healthyCount / Math.max(devices.length, 1)) * 360}deg ${((healthyCount + warningCount) / Math.max(devices.length, 1)) * 360}deg, #ef4444 ${((healthyCount + warningCount) / Math.max(devices.length, 1)) * 360}deg 360deg)`,
                }}
              />
              <div style={{ fontSize: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4 }}>
                  <SeverityDot severity="healthy" /> Healthy: <strong>{healthyCount}</strong>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4 }}>
                  <SeverityDot severity="warning" /> Warning: <strong>{warningCount}</strong>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <SeverityDot severity="critical" /> Critical: <strong>{criticalCount}</strong>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
