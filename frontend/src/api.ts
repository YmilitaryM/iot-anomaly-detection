const BASE = '/api'

export interface SensorData {
  device_id: string
  sensor_id: string
  sensor_type: string
  value: number
  timestamp: string
  unit: string | null
}

export interface AlertEvent {
  event_id: string
  device_id: string
  sensor_id: string
  sensor_type: string
  timestamp: string
  anomaly_score: number
  severity: 'critical' | 'warning' | 'info'
  detection_source: string
  evidence: Record<string, unknown>
  status: string
}

export interface Device {
  device_id: string
  device_type: string
  training_status: string
  model_version: string
}

export async function fetchAlerts(limit = 50, offset = 0) {
  const res = await fetch(`${BASE}/alerts?limit=${limit}&offset=${offset}`)
  return res.json() as Promise<{ total: number; items: AlertEvent[] }>
}

export async function fetchDevices() {
  const res = await fetch(`${BASE}/devices`)
  return res.json() as Promise<{ total: number; items: Device[] }>
}

export async function fetchSensorHistory(
  deviceId: string, sensorId: string, start: string, end: string, limit = 500
) {
  const res = await fetch(
    `${BASE}/data/sensors/${deviceId}/${sensorId}?start=${start}&end=${end}&limit=${limit}`
  )
  return res.json() as Promise<{ count: number; data: SensorData[] }>
}

export async function submitFeedback(eventId: string, confirmed: boolean) {
  const res = await fetch(
    `${BASE}/alerts/${eventId}/feedback?confirmed=${confirmed}&operator=operator`,
    { method: 'POST' }
  )
  return res.json()
}
