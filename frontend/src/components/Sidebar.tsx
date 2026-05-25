import { useNavigate, useLocation } from 'react-router-dom'

interface SidebarItem {
  key: string
  label: string
}

interface SidebarSection {
  title: string
  items: SidebarItem[]
  parentRoute: string
}

const SIDEBAR_MAP: Record<string, SidebarSection> = {
  overview: {
    title: 'Overview',
    parentRoute: '/',
    items: [
      { key: '', label: 'Dashboard' },
      { key: 'health', label: 'Health Map' },
      { key: 'analytics', label: 'Analytics' },
    ],
  },
  devices: {
    title: 'Devices',
    parentRoute: '/devices',
    items: [
      { key: '', label: 'Device List' },
      { key: 'sensors', label: 'Sensor Config' },
      { key: 'explorer', label: 'Data Explorer' },
    ],
  },
  alerts: {
    title: 'Alerts',
    parentRoute: '/alerts',
    items: [
      { key: '', label: 'Alert Feed' },
      { key: 'feedback', label: 'Feedback Queue' },
    ],
  },
  training: {
    title: 'Training',
    parentRoute: '/training',
    items: [
      { key: '', label: 'Model Status' },
      { key: 'drift', label: 'Drift Monitor' },
    ],
  },
  settings: {
    title: 'Settings',
    parentRoute: '/settings',
    items: [
      { key: '', label: 'Notifications' },
      { key: 'global', label: 'Global Config' },
    ],
  },
}

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const sectionKey = location.pathname.split('/')[1] || 'overview'
  const subPath = location.pathname.split('/')[2] || ''
  const section = SIDEBAR_MAP[sectionKey] || SIDEBAR_MAP.overview

  return (
    <aside className="sidebar">
      <div className="sidebar-section-title">{section.title}</div>
      {section.items.map(item => (
        <button
          key={item.key}
          className={`sidebar-item ${subPath === item.key ? 'active' : ''}`}
          onClick={() => {
            const path = item.key
              ? `${section.parentRoute}/${item.key}`
              : section.parentRoute || '/'
            navigate(path)
          }}
        >
          {item.label}
        </button>
      ))}
    </aside>
  )
}

export { SIDEBAR_MAP }
