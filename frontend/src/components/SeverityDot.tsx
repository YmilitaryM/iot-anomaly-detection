type Severity = 'critical' | 'warning' | 'info' | 'healthy'

interface SeverityDotProps {
  severity: Severity
}

export default function SeverityDot({ severity }: SeverityDotProps) {
  return <span className={`severity-dot ${severity}`} />
}
