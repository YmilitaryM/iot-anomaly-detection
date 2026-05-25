import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import TopNav from '../TopNav'

describe('TopNav', () => {
  it('renders all section buttons', () => {
    render(
      <MemoryRouter>
        <TopNav wsConnected={true} alertCount={5} deviceCount={3} />
      </MemoryRouter>
    )
    expect(screen.getByText('Overview')).toBeInTheDocument()
    expect(screen.getByText('Devices')).toBeInTheDocument()
    expect(screen.getByText('Alerts')).toBeInTheDocument()
  })

  it('shows connected status', () => {
    render(
      <MemoryRouter>
        <TopNav wsConnected={true} alertCount={0} deviceCount={0} />
      </MemoryRouter>
    )
    expect(screen.getByText('Live')).toBeInTheDocument()
  })

  it('shows disconnected status', () => {
    render(
      <MemoryRouter>
        <TopNav wsConnected={false} alertCount={0} deviceCount={0} />
      </MemoryRouter>
    )
    expect(screen.getByText('Disconnected')).toBeInTheDocument()
  })
})
