import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import SettingsPage from '../SettingsPage'

describe('SettingsPage', () => {
  it('renders settings heading', () => {
    render(<SettingsPage />)
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('renders notification channels', () => {
    render(<SettingsPage />)
    expect(screen.getByText('DingTalk')).toBeInTheDocument()
    expect(screen.getByText('Email')).toBeInTheDocument()
  })

  it('renders global parameters', () => {
    render(<SettingsPage />)
    expect(screen.getByText('Alert Cooldown (min)')).toBeInTheDocument()
  })
})
