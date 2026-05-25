import { useEffect, useRef, useState, useCallback } from 'react'
import type { AlertEvent } from './api'

export function useWebSocket(onAlert: (alert: AlertEvent) => void) {
  const [connected, setConnected] = useState(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined)
  const attemptsRef = useRef(0)

  const connect = useCallback(() => {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:'
    const ws = new WebSocket(`${protocol}//${location.host}/ws/alerts`)
    wsRef.current = ws

    ws.onopen = () => {
      setConnected(true)
      attemptsRef.current = 0
    }
    ws.onclose = () => {
      setConnected(false)
      const delay = Math.min(1000 * 2 ** attemptsRef.current + Math.random() * 1000, 30000)
      attemptsRef.current++
      reconnectTimerRef.current = setTimeout(connect, delay)
    }
    ws.onerror = () => ws.close()
    ws.onmessage = (e) => {
      try { onAlert(JSON.parse(e.data)) } catch { /* skip */ }
    }
  }, [onAlert])

  useEffect(() => {
    connect()
    return () => {
      clearTimeout(reconnectTimerRef.current)
      wsRef.current?.close()
    }
  }, [connect])

  return connected
}
