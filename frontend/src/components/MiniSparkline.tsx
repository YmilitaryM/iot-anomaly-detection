import { useMemo } from 'react'

interface MiniSparklineProps {
  data: number[]
  color?: string
  width?: number
  height?: number
}

export default function MiniSparkline({ data, color = '#38bdf8', width = 80, height = 20 }: MiniSparklineProps) {
  const pathD = useMemo(() => {
    if (data.length < 2) return ''
    const max = Math.max(...data)
    const min = Math.min(...data)
    const range = max - min || 1
    const xStep = width / (data.length - 1)
    return data.map((v, i) => {
      const x = i * xStep
      const y = height - ((v - min) / range) * (height - 2) - 1
      return `${i === 0 ? 'M' : 'L'}${x},${y}`
    }).join(' ')
  }, [data, width, height])

  return (
    <svg width={width} height={height} style={{ display: 'block' }}>
      <path d={pathD} fill="none" stroke={color} strokeWidth="1" />
    </svg>
  )
}
