import { describe, it, expect, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import { usePolling } from '../usePolling'

describe('usePolling', () => {
  it('calls callback immediately', () => {
    const cb = vi.fn()
    renderHook(() => usePolling(cb, 5000))
    expect(cb).toHaveBeenCalledTimes(1)
  })

  it('does not call when disabled', () => {
    const cb = vi.fn()
    renderHook(() => usePolling(cb, 5000, false))
    expect(cb).not.toHaveBeenCalled()
  })
})
