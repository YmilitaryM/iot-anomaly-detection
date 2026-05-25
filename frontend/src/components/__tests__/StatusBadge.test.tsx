import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatusBadge from '../StatusBadge'

describe('StatusBadge', () => {
  it('renders the label', () => {
    render(<StatusBadge variant="critical" label="CRIT" />)
    expect(screen.getByText('CRIT')).toBeInTheDocument()
  })

  it('applies variant class', () => {
    const { container } = render(<StatusBadge variant="warning" label="WARN" />)
    expect(container.firstChild).toHaveClass('status-badge')
    expect(container.firstChild).toHaveClass('warning')
  })
})
