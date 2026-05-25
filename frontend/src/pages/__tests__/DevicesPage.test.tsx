import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DevicesPage from '../DevicesPage'

vi.mock('../../api', () => ({
  fetchDevices: vi.fn().mockResolvedValue({
    items: [{ device_id: 'pump-001', device_type: 'Pump', training_status: 'active', model_version: 'v1' }],
  }),
}))

describe('DevicesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders search bar', () => {
    render(
      <MemoryRouter>
        <DevicesPage />
      </MemoryRouter>
    )
    expect(screen.getByPlaceholderText('Search devices...')).toBeInTheDocument()
  })

  it('shows device in table after load', async () => {
    render(
      <MemoryRouter>
        <DevicesPage />
      </MemoryRouter>
    )
    expect(await screen.findByText('pump-001')).toBeInTheDocument()
  })
})
