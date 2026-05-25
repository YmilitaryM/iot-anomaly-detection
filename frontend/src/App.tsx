import { useState, useCallback, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import TopNav from './components/TopNav'
import Sidebar from './components/Sidebar'
import OverviewPage from './pages/OverviewPage'
import DevicesPage from './pages/DevicesPage'
import DeviceDetail from './pages/DeviceDetail'
import AlertsPage from './pages/AlertsPage'
import AlertDetail from './pages/AlertDetail'
import TrainingPage from './pages/TrainingPage'
import SettingsPage from './pages/SettingsPage'
import { fetchAlerts, fetchDevices, type AlertEvent, type Device } from './api'
import { useWebSocket } from './useWebSocket'
import './App.css'

function App() {
  const [alerts, setAlerts] = useState<AlertEvent[]>([])
  const [devices, setDevices] = useState<Device[]>([])

  const onAlert = useCallback((a: AlertEvent) => {
    setAlerts(prev => [a, ...prev].slice(0, 200))
  }, [])
  const wsConnected = useWebSocket(onAlert)

  useEffect(() => {
    fetchAlerts().then(r => setAlerts(r.items)).catch(err => console.error('Failed to fetch alerts:', err))
    fetchDevices().then(r => setDevices(r.items)).catch(err => console.error('Failed to fetch devices:', err))
  }, [])

  useEffect(() => {
    const i = setInterval(() => {
      fetchDevices().then(r => setDevices(r.items)).catch(err => console.error('Failed to fetch devices:', err))
    }, 5000)
    return () => clearInterval(i)
  }, [])

  return (
    <BrowserRouter>
      <div className="app-shell">
        <TopNav
          wsConnected={wsConnected}
          alertCount={alerts.length}
          deviceCount={devices.length}
        />
        <div className="app-body">
          <Sidebar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<OverviewPage alerts={alerts} devices={devices} />} />
              <Route path="/overview" element={<Navigate to="/" replace />} />
              <Route path="/devices" element={<DevicesPage />} />
              <Route path="/devices/:deviceId" element={<DeviceDetail />} />
              <Route path="/alerts" element={<AlertsPage alerts={alerts} />} />
              <Route path="/alerts/:eventId" element={<AlertDetail alerts={alerts} />} />
              <Route path="/training" element={<TrainingPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
