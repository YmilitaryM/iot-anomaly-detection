import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import MiniSparkline from '../MiniSparkline'

describe('MiniSparkline', () => {
  it('renders an svg', () => {
    const { container } = render(<MiniSparkline data={[1, 2, 3, 4, 5]} />)
    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('renders a path element', () => {
    const { container } = render(<MiniSparkline data={[1, 2, 3]} />)
    expect(container.querySelector('path')).toBeInTheDocument()
  })

  it('renders nothing when data has less than 2 points', () => {
    const { container } = render(<MiniSparkline data={[1]} />)
    expect(container.querySelector('path')?.getAttribute('d')).toBe('')
  })
})
