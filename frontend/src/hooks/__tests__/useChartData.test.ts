import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'

vi.mock('../../api', () => ({
  fetchSensorHistory: vi.fn().mockResolvedValue({
    data: [{ timestamp: '2026-05-25T10:00:00Z', value: 25.0 }],
  }),
}))

import { useChartData } from '../useChartData'

describe('useChartData', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns empty data when deviceId is empty', () => {
    const { result } = renderHook(() => useChartData('', ''))
    expect(result.current.data).toEqual([])
  })

  it('fetches data when device and sensor are provided', async () => {
    const { result } = renderHook(() => useChartData('pump-001', 'temp-01'))
    await waitFor(() => {
      expect(result.current.data.length).toBeGreaterThan(0)
    })
  })
})
