import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import TrainingPage from '../TrainingPage'

describe('TrainingPage', () => {
  it('renders model status heading', () => {
    render(<TrainingPage />)
    expect(screen.getByText('Model Status')).toBeInTheDocument()
  })

  it('renders Pump Model card', () => {
    render(<TrainingPage />)
    expect(screen.getByText('Pump Model')).toBeInTheDocument()
  })

  it('renders drift chart section', () => {
    render(<TrainingPage />)
    expect(screen.getByText('Concept Drift — KL Divergence (Pump Model)')).toBeInTheDocument()
  })
})
