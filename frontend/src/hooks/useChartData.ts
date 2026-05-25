import { useState, useEffect, useRef } from 'react'
import { fetchSensorHistory, type SensorData } from '../api'

export function useChartData(deviceId: string, sensorId: string, lookbackMs: number = 3600000) {
  const [data, setData] = useState<SensorData[]>([])
  const [loading, setLoading] = useState(false)
  const timerRef = useRef<ReturnType<typeof setInterval> | undefined>(undefined)
  const genRef = useRef(0)

  useEffect(() => {
    if (!deviceId || !sensorId) {
      setData([])
      return
    }

    let cancelled = false
    genRef.current++

    const fetchData = () => {
      const end = new Date().toISOString()
      const start = new Date(Date.now() - lookbackMs).toISOString()
      setLoading(true)
      fetchSensorHistory(deviceId, sensorId, start, end).then(r => {
        if (!cancelled) {
          setData(r.data || [])
          setLoading(false)
        }
      }).catch(() => {
        if (!cancelled) setLoading(false)
      })
    }

    fetchData()
    timerRef.current = setInterval(fetchData, 5000)
    return () => {
      cancelled = true
      clearInterval(timerRef.current)
    }
  }, [deviceId, sensorId, lookbackMs])

  return { data, loading }
}
