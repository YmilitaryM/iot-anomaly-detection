import { useNavigate, useLocation } from 'react-router-dom'

interface Section {
  key: string
  label: string
  color: string
}

const SECTIONS: Section[] = [
  { key: 'overview', label: 'Overview', color: '#38bdf8' },
  { key: 'devices', label: 'Devices', color: '#f97316' },
  { key: 'alerts', label: 'Alerts', color: '#ef4444' },
  { key: 'training', label: 'Training', color: '#8b5cf6' },
  { key: 'settings', label: 'Settings', color: '#38bdf8' },
]

interface TopNavProps {
  wsConnected: boolean
  alertCount: number
  deviceCount: number
}

export default function TopNav({ wsConnected, alertCount, deviceCount }: TopNavProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const activeSection = location.pathname.split('/')[1] || 'overview'

  return (
    <header className="topnav">
      <span className="topnav-logo">IoT Sentinel</span>
      <div className="topnav-sections">
        {SECTIONS.map(s => (
          <button
            key={s.key}
            className={`topnav-section ${activeSection === s.key ? 'active' : ''}`}
            onClick={() => navigate(`/${s.key === 'overview' ? '' : s.key}`)}
            style={activeSection === s.key ? { color: s.color } : undefined}
          >
            {s.label}
          </button>
        ))}
      </div>
      <div className="topnav-right">
        <span className={`topnav-status-dot ${wsConnected ? 'connected' : ''}`} />
        <span>{wsConnected ? 'Live' : 'Disconnected'}</span>
        <span className="topnav-badge">Alerts: {alertCount}</span>
        <span className="topnav-badge">Devices: {deviceCount}</span>
      </div>
    </header>
  )
}

export { SECTIONS }
