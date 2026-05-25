import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatCard from '../StatCard'

describe('StatCard', () => {
  it('renders label and value', () => {
    render(<StatCard label="Critical" value={3} />)
    expect(screen.getByText('Critical')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('renders delta when provided', () => {
    render(<StatCard label="Warning" value={12} delta="+2" deltaPositive={false} />)
    expect(screen.getByText('+2')).toBeInTheDocument()
    expect(screen.getByText('+2')).toHaveClass('negative')
  })

  it('applies accent color as border-top', () => {
    const { container } = render(<StatCard label="Test" value={1} accentColor="#ef4444" />)
    expect(container.firstChild).toHaveStyle({ borderTopColor: '#ef4444' })
  })
})
