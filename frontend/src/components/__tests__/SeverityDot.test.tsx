import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import SeverityDot from '../SeverityDot'

describe('SeverityDot', () => {
  it('applies severity class', () => {
    const { container } = render(<SeverityDot severity="critical" />)
    expect(container.firstChild).toHaveClass('severity-dot')
    expect(container.firstChild).toHaveClass('critical')
  })
})
