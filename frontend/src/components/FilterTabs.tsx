interface FilterTabsProps {
  options: { key: string; label: string }[]
  selected: string
  onChange: (key: string) => void
}

export default function FilterTabs({ options, selected, onChange }: FilterTabsProps) {
  return (
    <div className="filter-tabs">
      {options.map(opt => (
        <button
          key={opt.key}
          className={`filter-tab ${selected === opt.key ? 'active' : ''}`}
          onClick={() => onChange(opt.key)}
        >
          {opt.label}
        </button>
      ))}
    </div>
  )
}
