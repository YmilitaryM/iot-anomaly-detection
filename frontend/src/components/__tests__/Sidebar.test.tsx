import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Sidebar from '../Sidebar'

describe('Sidebar', () => {
  it('renders items for current section', () => {
    render(
      <MemoryRouter initialEntries={['/alerts']}>
        <Sidebar />
      </MemoryRouter>
    )
    expect(screen.getByText('Alert Feed')).toBeInTheDocument()
    expect(screen.getByText('Feedback Queue')).toBeInTheDocument()
  })
})
