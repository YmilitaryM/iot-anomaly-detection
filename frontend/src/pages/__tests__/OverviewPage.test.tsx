import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import OverviewPage from '../OverviewPage'

vi.mock('../../api', () => ({
  fetchSensorHistory: vi.fn().mockResolvedValue({ data: [] }),
}))

describe('OverviewPage', () => {
  const mockAlerts = [
    { event_id: '1', device_id: 'pump-001', sensor_id: 'temp-01', sensor_type: 'temperature',
      anomaly_score: 0.95, severity: 'critical' as const, detection_source: 'statistical',
      timestamp: '2026-05-25T10:00:00Z', evidence: {}, status: 'open' },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders dashboard title', () => {
    render(
      <MemoryRouter>
        <OverviewPage alerts={[]} devices={[]} />
      </MemoryRouter>
    )
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('shows alert in feed', () => {
    render(
      <MemoryRouter>
        <OverviewPage alerts={mockAlerts} devices={[]} />
      </MemoryRouter>
    )
    expect(screen.getByText('pump-001 / temp-01')).toBeInTheDocument()
  })

  it('shows empty state when no alerts', () => {
    render(
      <MemoryRouter>
        <OverviewPage alerts={[]} devices={[]} />
      </MemoryRouter>
    )
    expect(screen.getByText('No alerts yet')).toBeInTheDocument()
  })
})
