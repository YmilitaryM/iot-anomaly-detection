import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import EmptyState from '../EmptyState'

describe('EmptyState', () => {
  it('renders the message', () => {
    render(<EmptyState message="No data yet" />)
    expect(screen.getByText('No data yet')).toBeInTheDocument()
  })

  it('renders default icon', () => {
    render(<EmptyState message="Empty" />)
    expect(screen.getByText('—')).toBeInTheDocument()
  })
})
