import ReactECharts from 'echarts-for-react'
import type { EChartsOption } from 'echarts'

interface SeriesConfig {
  name: string
  color: string
  data: [string, number][]
  lineStyle?: 'solid' | 'dashed'
}

interface TimeSeriesChartProps {
  series: SeriesConfig[]
  height?: number
  title?: string
  anomalyWindows?: { start: string; end: string }[]
  anomalyPoints?: { time: string; value: number }[]
}

const SENSOR_COLORS: Record<string, string> = {
  temperature: '#f97316', vibration: '#e11d48', current: '#facc15',
  pressure: '#60a5fa', humidity: '#22d3ee', power: '#f59e0b',
  discrete: '#8b5cf6',
}

export default function TimeSeriesChart({
  series, height = 300, title, anomalyWindows, anomalyPoints,
}: TimeSeriesChartProps) {
  const option: EChartsOption = {
    tooltip: { trigger: 'axis' as const },
    legend: {
      data: series.map(s => s.name),
      bottom: 0,
      textStyle: { color: '#94a3b8', fontSize: 10 },
    },
    grid: { left: 50, right: 20, top: title ? 30 : 15, bottom: 30 },
    xAxis: {
      type: 'time' as const,
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { show: false },
    },
    yAxis: {
      type: 'value' as const,
      axisLabel: { color: '#94a3b8', fontSize: 10 },
      splitLine: { lineStyle: { color: '#1e293b' } },
    },
    series: [
      ...(anomalyWindows?.map((w, i) => ({
        type: 'line' as const,
        name: `anomaly-${i}`,
        data: [] as [string, number][],
        markArea: {
          silent: true,
          itemStyle: { color: 'rgba(239,68,68,0.06)' },
          data: [[{ xAxis: w.start }, { xAxis: w.end }]],
        },
      })) || []),
      ...series.map(s => ({
        type: 'line' as const,
        name: s.name,
        data: s.data,
        smooth: true,
        showSymbol: false,
        lineStyle: {
          color: s.color || SENSOR_COLORS[s.name] || '#38bdf8',
          width: 1.5,
          type: s.lineStyle === 'dashed' ? 'dashed' as const : 'solid' as const,
        },
      })),
      ...(anomalyPoints && anomalyPoints.length > 0
        ? [{
            type: 'scatter' as const,
            name: 'anomaly',
            data: anomalyPoints.map(p => [p.time, p.value]),
            symbolSize: 8,
            itemStyle: { color: '#ef4444', borderColor: '#0f172a', borderWidth: 2 },
          }]
        : []),
    ] as any,
  }

  return (
    <div className="chart-container">
      {title && <div className="chart-title">{title}</div>}
      <ReactECharts option={option} style={{ height }} />
    </div>
  )
}

export { SENSOR_COLORS }
