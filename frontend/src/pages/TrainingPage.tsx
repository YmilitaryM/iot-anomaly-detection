import TimeSeriesChart from '../components/TimeSeriesChart'

interface ModelInfo {
  name: string
  status: 'active' | 'accumulating' | 'degraded'
  version: string
  dataPoints: number
  minRequired: number
  lastTrained: string
  latency: string
  reconError: number
}

const MOCK_MODELS: ModelInfo[] = [
  { name: 'Pump Model', status: 'active', version: 'v2.3.1', dataPoints: 850000, minRequired: 65000, lastTrained: 'May 20, 2026', latency: '0.4ms', reconError: 0.012 },
  { name: 'Fan Model', status: 'accumulating', version: '—', dataPoints: 12000, minRequired: 65000, lastTrained: 'Never', latency: '—', reconError: 0 },
]

// KL divergence mock data
const driftData: [string, number][] = [
  ['2026-05-01', 0.042], ['2026-05-03', 0.038], ['2026-05-06', 0.045],
  ['2026-05-09', 0.041], ['2026-05-12', 0.036], ['2026-05-15', 0.044],
  ['2026-05-18', 0.048], ['2026-05-21', 0.052], ['2026-05-24', 0.058], ['2026-05-25', 0.065],
]

export default function TrainingPage() {
  return (
    <div>
      <h2 style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 600, marginBottom: 12 }}>Model Status</h2>

      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        {MOCK_MODELS.map(m => (
          <div key={m.name} className="section-card" style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ color: '#e2e8f0', fontWeight: 600, fontSize: 11 }}>{m.name}</span>
              <span style={{
                padding: '2px 8px', borderRadius: 8, fontSize: 8,
                background: m.status === 'active' ? '#14532d' : '#7c2d12',
                color: m.status === 'active' ? '#86efac' : '#fdba74',
              }}>
                {m.status === 'active' ? 'Active' : 'Accumulating'}
              </span>
            </div>
            <div style={{ fontSize: 10, color: '#64748b', display: 'flex', flexDirection: 'column', gap: 3 }}>
              <div>Version: <span style={{ color: '#94a3b8' }}>{m.version}</span></div>
              <div>Training data: <span style={{ color: '#94a3b8' }}>{m.dataPoints.toLocaleString()} pts</span></div>
              <div>Last trained: <span style={{ color: '#94a3b8' }}>{m.lastTrained}</span></div>
              <div>Inference: <span style={{ color: '#94a3b8' }}>{m.latency}</span></div>
              {m.status === 'accumulating' && (
                <div style={{ marginTop: 4 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 8, marginBottom: 2 }}>
                    <span>Progress</span>
                    <span style={{ color: '#f97316' }}>{Math.round((m.dataPoints / m.minRequired) * 100)}%</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-bar-fill" style={{ width: `${(m.dataPoints / m.minRequired) * 100}%`, background: '#f97316' }} />
                  </div>
                </div>
              )}
              {m.status === 'active' && (
                <div style={{ marginTop: 4 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 8, marginBottom: 2 }}>
                    <span>Recon Error</span><span style={{ color: '#22c55e' }}>{m.reconError}</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-bar-fill" style={{ width: `${m.reconError * 1000}%`, background: '#22c55e' }} />
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="section-card">
        <div className="chart-header">
          <span className="chart-title">Concept Drift — KL Divergence (Pump Model)</span>
          <span style={{ fontSize: 9, color: '#64748b' }}>30-day window</span>
        </div>
        <TimeSeriesChart
          series={[{ name: 'KL Divergence', color: '#8b5cf6', data: driftData }]}
          height={200}
        />
      </div>
    </div>
  )
}
