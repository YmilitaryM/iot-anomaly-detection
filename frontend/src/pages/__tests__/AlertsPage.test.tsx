import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AlertsPage from '../AlertsPage'

const mockAlerts = [{
  event_id: '1', device_id: 'pump-001', sensor_id: 'temp-01', sensor_type: 'temperature',
  anomaly_score: 0.95, severity: 'critical' as const, detection_source: 'statistical',
  timestamp: '2026-05-25T10:00:00Z', evidence: {}, status: 'open',
}]

describe('AlertsPage', () => {
  it('renders filter tabs', () => {
    render(
      <MemoryRouter>
        <AlertsPage alerts={mockAlerts} />
      </MemoryRouter>
    )
    expect(screen.getByText('Critical')).toBeInTheDocument()
    expect(screen.getByText('Open')).toBeInTheDocument()
  })

  it('shows alert in table', () => {
    render(
      <MemoryRouter>
        <AlertsPage alerts={mockAlerts} />
      </MemoryRouter>
    )
    expect(screen.getByText('pump-001')).toBeInTheDocument()
  })

  it('shows empty state when no alerts', () => {
    render(
      <MemoryRouter>
        <AlertsPage alerts={[]} />
      </MemoryRouter>
    )
    expect(screen.getByText('No alerts match your filters')).toBeInTheDocument()
  })
})
