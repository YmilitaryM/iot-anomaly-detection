import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Route, Routes } from 'react-router-dom'
import DeviceDetail from '../DeviceDetail'

vi.mock('echarts-for-react', () => ({
  default: () => null,
}))

vi.mock('../../api', () => ({
  fetchSensorHistory: vi.fn().mockResolvedValue({ data: [] }),
}))

describe('DeviceDetail', () => {
  it('renders device id from route', async () => {
    render(
      <MemoryRouter initialEntries={['/devices/pump-001']}>
        <Routes>
          <Route path="/devices/:deviceId" element={<DeviceDetail />} />
        </Routes>
      </MemoryRouter>
    )
    expect(await screen.findByText('pump-001')).toBeInTheDocument()
  })

  it('shows back button', async () => {
    render(
      <MemoryRouter initialEntries={['/devices/pump-001']}>
        <Routes>
          <Route path="/devices/:deviceId" element={<DeviceDetail />} />
        </Routes>
      </MemoryRouter>
    )
    expect(await screen.findByText('← Back to Devices')).toBeInTheDocument()
  })
})
