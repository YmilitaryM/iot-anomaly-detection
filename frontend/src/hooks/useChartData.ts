import { useState, useEffect, useRef } from 'react'
import { fetchSensorHistory, type SensorData } from '../api'

export function useChartData(deviceId: string, sensorId: string, lookbackMs: number = 3600000) {
  const [data, setData] = useState<SensorData[]>([])
  const [loading, setLoading] = useState(false)
  const timerRef = useRef<ReturnType<typeof setInterval>>()

  useEffect(() => {
    if (!deviceId || !sensorId) {
      setData([])
      return
    }

    const fetchData = () => {
      const end = new Date().toISOString()
      const start = new Date(Date.now() - lookbackMs).toISOString()
      setLoading(true)
      fetchSensorHistory(deviceId, sensorId, start, end).then(r => {
        setData(r.data || [])
        setLoading(false)
      }).catch(() => setLoading(false))
    }

    fetchData()
    timerRef.current = setInterval(fetchData, 5000)
    return () => clearInterval(timerRef.current)
  }, [deviceId, sensorId, lookbackMs])

  return { data, loading }
}
