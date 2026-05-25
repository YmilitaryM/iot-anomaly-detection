import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Route, Routes } from 'react-router-dom'
import AlertDetail from '../AlertDetail'

const mockAlerts = [{
  event_id: 'c88d1cbb-2737', device_id: 'pump-001', sensor_id: 'temp-01',
  sensor_type: 'temperature', anomaly_score: 0.95, severity: 'critical' as const,
  detection_source: 'statistical', timestamp: '2026-05-25T10:00:00Z',
  evidence: { value: 85.0, mean: 29.9, std: 2.3, z_score: 10.83, sigma: 3.0, window_size: 60 },
  status: 'open',
}]

describe('AlertDetail', () => {
  it('renders alert severity', async () => {
    render(
      <MemoryRouter initialEntries={['/alerts/c88d1cbb-2737']}>
        <Routes>
          <Route path="/alerts/:eventId" element={<AlertDetail alerts={mockAlerts} />} />
        </Routes>
      </MemoryRouter>
    )
    expect(await screen.findByText('Critical')).toBeInTheDocument()
  })

  it('shows confirm and reject buttons', async () => {
    render(
      <MemoryRouter initialEntries={['/alerts/c88d1cbb-2737']}>
        <Routes>
          <Route path="/alerts/:eventId" element={<AlertDetail alerts={mockAlerts} />} />
        </Routes>
      </MemoryRouter>
    )
    expect(await screen.findByText('✓ Confirm')).toBeInTheDocument()
    expect(screen.getByText('✗ Reject')).toBeInTheDocument()
  })

  it('shows empty state for unknown event id', () => {
    render(
      <MemoryRouter initialEntries={['/alerts/unknown-id']}>
        <Routes>
          <Route path="/alerts/:eventId" element={<AlertDetail alerts={[]} />} />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.getByText('Alert not found')).toBeInTheDocument()
  })
})
