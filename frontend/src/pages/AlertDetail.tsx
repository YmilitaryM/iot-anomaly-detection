import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import TimeSeriesChart from '../components/TimeSeriesChart'
import EmptyState from '../components/EmptyState'
import { submitFeedback, type AlertEvent } from '../api'

interface AlertDetailProps {
  alerts: AlertEvent[]
}

export default function AlertDetail({ alerts }: AlertDetailProps) {
  const { eventId } = useParams<{ eventId: string }>()
  const navigate = useNavigate()
  const [note, setNote] = useState('')
  const [feedbackStatus, setFeedbackStatus] = useState<string>()

  const alert = alerts.find(a => a.event_id === eventId)

  if (!alert) {
    return <EmptyState icon="🔍" message="Alert not found" />
  }

  const evidence = (alert.evidence || {}) as Record<string, unknown>
  const evidenceKeys = Object.keys(evidence).filter(k => k !== 'roc_violation')

  const formatEvidence = (v: unknown) => {
    if (typeof v === 'number') return v.toFixed(4)
    if (typeof v === 'boolean') return v ? 'true' : 'false'
    return String(v)
  }

  const handleFeedback = async (confirmed: boolean) => {
    try {
      await submitFeedback(alert.event_id, confirmed)
      setFeedbackStatus(confirmed ? 'confirmed' : 'rejected')
    } catch {
      // Show error toast in production
    }
  }

  // Mock chart data around alert time
  const alertTime = new Date(alert.timestamp)
  const chartData: [string, number][] = Array.from({ length: 40 }, (_, i) => [
    new Date(alertTime.getTime() + (i - 20) * 60000).toISOString(),
    28 + Math.sin(i * 0.3) * 3 + (i === 20 ? 55 : 0),
  ])

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <button onClick={() => navigate('/alerts')} style={{ background: 'none', border: 'none', color: '#64748b', fontSize: 11, cursor: 'pointer' }}>
          ← Back to Alerts
        </button>
        <span style={{ color: '#334155' }}>|</span>
        <span style={{ color: '#e2e8f0', fontWeight: 600, fontSize: 12 }}>Alert Detail</span>
        <span style={{ color: '#64748b', fontSize: 10, fontFamily: 'monospace' }}>{alert.event_id.slice(0, 8)}...</span>
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <div style={{ flex: 2 }}>
          <div className="section-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 8 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 16, fontWeight: 700, color: alert.severity === 'critical' ? '#ef4444' : alert.severity === 'warning' ? '#f97316' : '#3b82f6' }}>
                    {alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}
                  </span>
                  <span style={{ background: '#7f1d1d', color: '#fca5a5', padding: '2px 8px', borderRadius: 4, fontSize: 9 }}>
                    Score: {alert.anomaly_score.toFixed(2)}
                  </span>
                </div>
                <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 4 }}>
                  {alert.device_id} / {alert.sensor_id} · {new Date(alert.timestamp).toLocaleString()}
                </div>
              </div>
              <span style={{ fontSize: 10, color: '#64748b' }}>Detection: {alert.detection_source}</span>
            </div>

            <div className="evidence-panel">
              <div className="evidence-panel-title">Evidence</div>
              <div className="evidence-grid">
                {evidenceKeys.map(k => (
                  <div key={k}>
                    <div className="evidence-item-label">{k}</div>
                    <div className="evidence-item-value">
                      {formatEvidence(evidence[k])}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <TimeSeriesChart
            series={[{ name: alert.sensor_id, color: '#38bdf8', data: chartData }]}
            height={200}
            title="Context Window — ±30 min around event"
            anomalyPoints={[{ time: alert.timestamp, value: alert.evidence && typeof alert.evidence === 'object' && 'value' in alert.evidence ? Number(alert.evidence.value) : 85 }]}
          />
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div className="section-card">
            <div className="section-card-title">Feedback</div>
            <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
              <button className="feedback-confirm" onClick={() => handleFeedback(true)}>✓ Confirm</button>
              <button className="feedback-reject" onClick={() => handleFeedback(false)}>✗ Reject</button>
            </div>
            <div style={{ marginTop: 8 }}>
              <input className="form-input" placeholder="Add note (optional)" value={note} onChange={e => setNote(e.target.value)} />
            </div>
            {feedbackStatus && (
              <div style={{ marginTop: 8, fontSize: 10, color: feedbackStatus === 'confirmed' ? '#86efac' : '#fca5a5' }}>
                {feedbackStatus === 'confirmed' ? '✓ Confirmed' : '✗ Rejected'}
              </div>
            )}
          </div>

          <div className="section-card">
            <div className="section-card-title">Alert Info</div>
            <div style={{ fontSize: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                <span style={{ color: '#64748b' }}>Event ID</span>
                <span style={{ color: '#94a3b8', fontFamily: 'monospace' }}>{alert.event_id.slice(0, 13)}...</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                <span style={{ color: '#64748b' }}>Source</span>
                <span style={{ color: '#94a3b8' }}>{alert.detection_source}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#64748b' }}>Status</span>
                <span style={{ color: alert.status === 'open' ? '#fca5a5' : '#86efac' }}>{alert.status}</span>
              </div>
            </div>
          </div>

          <div className="section-card">
            <div className="section-card-title">Related Alerts</div>
            {alerts.filter(a => a.device_id === alert.device_id && a.sensor_id === alert.sensor_id && a.event_id !== alert.event_id).slice(0, 3).map(a => (
              <div key={a.event_id} style={{ fontSize: 9, color: '#94a3b8', marginTop: 3 }}>
                {a.severity.toUpperCase()} {a.anomaly_score.toFixed(2)} · {new Date(a.timestamp).toLocaleTimeString()}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
