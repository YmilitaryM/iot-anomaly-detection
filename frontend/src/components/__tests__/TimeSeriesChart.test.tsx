import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import TimeSeriesChart from '../TimeSeriesChart'

describe('TimeSeriesChart', () => {
  const mockSeries = [{
    name: 'temp-01',
    color: '#f97316',
    data: [['2026-05-25T10:00:00Z', 25.0], ['2026-05-25T10:01:00Z', 26.0]] as [string, number][],
  }]

  it('renders chart container', () => {
    const { container } = render(<TimeSeriesChart series={mockSeries} />)
    expect(container.querySelector('.chart-container')).toBeInTheDocument()
  })

  it('renders title when provided', () => {
    render(<TimeSeriesChart series={mockSeries} title="Temperature" />)
    expect(document.body.textContent).toContain('Temperature')
  })

  it('renders with anomaly windows', () => {
    const { container } = render(
      <TimeSeriesChart
        series={mockSeries}
        anomalyWindows={[{ start: '2026-05-25T10:00:30Z', end: '2026-05-25T10:00:45Z' }]}
      />
    )
    expect(container.querySelector('.chart-container')).toBeInTheDocument()
  })

  it('renders with anomaly points', () => {
    const { container } = render(
      <TimeSeriesChart
        series={mockSeries}
        anomalyPoints={[{ time: '2026-05-25T10:00:30Z', value: 85.0 }]}
      />
    )
    expect(container.querySelector('.chart-container')).toBeInTheDocument()
  })
})
