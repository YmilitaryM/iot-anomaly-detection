import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import FilterTabs from '../FilterTabs'

describe('FilterTabs', () => {
  const options = [
    { key: 'all', label: 'All' },
    { key: 'critical', label: 'Critical' },
  ]

  it('renders all options', () => {
    render(<FilterTabs options={options} selected="all" onChange={() => {}} />)
    expect(screen.getByText('All')).toBeInTheDocument()
    expect(screen.getByText('Critical')).toBeInTheDocument()
  })

  it('marks selected option as active', () => {
    render(<FilterTabs options={options} selected="critical" onChange={() => {}} />)
    expect(screen.getByText('Critical')).toHaveClass('active')
  })

  it('calls onChange when clicked', async () => {
    const onChange = vi.fn()
    render(<FilterTabs options={options} selected="all" onChange={onChange} />)
    await userEvent.click(screen.getByText('Critical'))
    expect(onChange).toHaveBeenCalledWith('critical')
  })
})
