type BadgeVariant = 'critical' | 'warning' | 'info' | 'healthy'

interface StatusBadgeProps {
  variant: BadgeVariant
  label: string
}

export default function StatusBadge({ variant, label }: StatusBadgeProps) {
  return <span className={`status-badge ${variant}`}>{label}</span>
}
