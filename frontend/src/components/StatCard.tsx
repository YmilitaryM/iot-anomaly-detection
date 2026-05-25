import MiniSparkline from './MiniSparkline'

interface StatCardProps {
  label: string
  value: string | number
  delta?: string
  deltaPositive?: boolean
  accentColor?: string
  sparklineData?: number[]
}

export default function StatCard({ label, value, delta, deltaPositive, accentColor, sparklineData }: StatCardProps) {
  return (
    <div className="stat-card" style={accentColor ? { borderTopColor: accentColor } : undefined}>
      <div className="stat-card-label">{label}</div>
      <div className="stat-card-value">
        {value}
        {delta && (
          <span className={`stat-card-delta ${deltaPositive ? 'positive' : 'negative'}`}>
            {delta}
          </span>
        )}
      </div>
      {sparklineData && sparklineData.length >= 2 && (
        <MiniSparkline data={sparklineData} color={accentColor} height={16} />
      )}
    </div>
  )
}
