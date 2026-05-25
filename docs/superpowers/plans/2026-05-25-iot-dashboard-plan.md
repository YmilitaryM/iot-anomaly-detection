# IoT Dashboard Redesign — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the single-file dashboard prototype with a full 5-page management console using Industrial Dark theme, top-nav + sidebar architecture, reusable component library, and ECharts time-series charts.

**Architecture:** React + TypeScript + Vite SPA with react-router-dom v7 for client-side routing. ECharts via echarts-for-react for all charts. CSS variables for theme tokens (colors, spacing, radii). Components split into `components/` (reusable) and `pages/` (route-level). Custom hooks in `hooks/` for polling and chart data fetching. Existing WebSocket hook and API client are reused with extensions.

**Tech Stack:** React 19, TypeScript 6, Vite 8, react-router-dom 7, echarts + echarts-for-react, vitest + @testing-library/react for tests.

---

### Task 1: Install dependencies and set up test infrastructure

**Files:**
- Modify: `frontend/package.json`

- [ ] **Step 1: Install runtime dependencies**

```bash
cd frontend && npm install react-router-dom echarts echarts-for-react
```

- [ ] **Step 2: Install dev dependencies for testing**

```bash
cd frontend && npm install -D vitest @testing-library/react @testing-library/jest-dom @testing-library/user-event jsdom
```

- [ ] **Step 3: Add test script to package.json**

Edit `frontend/package.json`, add to `"scripts"`:
```json
"test": "vitest run",
"test:watch": "vitest"
```

- [ ] **Step 4: Add vitest config to vite.config.ts**

Append to `frontend/vite.config.ts`:
```typescript
/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:8010',
      '/ws': { target: 'ws://localhost:8010', ws: true },
    },
  },
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test-setup.ts',
  },
})
```

- [ ] **Step 5: Create test setup file**

Create `frontend/src/test-setup.ts`:
```typescript
import '@testing-library/jest-dom/vitest'
```

- [ ] **Step 6: Verify setup**

```bash
cd frontend && npx vitest run --passWithNoTests
```
Expected: "No test files found, exiting with code 0"

- [ ] **Step 7: Commit**

```bash
git add frontend/package.json frontend/package-lock.json frontend/vite.config.ts frontend/src/test-setup.ts
git commit -m "chore: add react-router, echarts, vitest, and testing-library dependencies"
```

---

### Task 2: CSS theme system — variables and global styles

**Files:**
- Rewrite: `frontend/src/App.css`
- Create: `frontend/src/index.css`

- [ ] **Step 1: Create CSS variables file**

Create `frontend/src/index.css`:
```css
:root {
  /* Background */
  --color-bg-primary: #0f172a;
  --color-bg-secondary: #1e293b;
  --color-bg-tertiary: #334155;
  --color-bg-input: #0f172a;

  /* Text */
  --color-text-primary: #e2e8f0;
  --color-text-secondary: #94a3b8;
  --color-text-muted: #64748b;
  --color-text-disabled: #475569;

  /* Accent */
  --color-accent: #38bdf8;
  --color-accent-bg: #1e3a5f;

  /* Severity */
  --color-critical: #ef4444;
  --color-critical-bg: #7f1d1d;
  --color-critical-text: #fca5a5;
  --color-warning: #f97316;
  --color-warning-bg: #7c2d12;
  --color-warning-text: #fdba74;
  --color-info: #3b82f6;
  --color-info-bg: #1e3a5f;
  --color-info-text: #93c5fd;
  --color-healthy: #22c55e;
  --color-healthy-bg: #14532d;
  --color-healthy-text: #86efac;

  /* Border */
  --color-border: #334155;
  --color-border-light: rgba(255,255,255,0.06);

  /* Spacing */
  --space-xs: 4px;
  --space-sm: 8px;
  --space-md: 12px;
  --space-lg: 16px;
  --space-xl: 24px;

  /* Radius */
  --radius-sm: 3px;
  --radius-md: 4px;
  --radius-lg: 8px;

  /* Font */
  --font-mono: 'JetBrains Mono', 'Fira Code', monospace;

  /* Layout */
  --topnav-height: 48px;
  --sidebar-width: 140px;

  /* Sensor type colors */
  --sensor-temperature: #f97316;
  --sensor-vibration: #e11d48;
  --sensor-current: #facc15;
  --sensor-pressure: #60a5fa;
  --sensor-humidity: #22d3ee;
  --sensor-power: #f59e0b;
  --sensor-discrete: #8b5cf6;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  font-size: 13px;
  line-height: 1.5;
}

#root {
  height: 100vh;
  display: flex;
  flex-direction: column;
}
```

- [ ] **Step 2: Rewrite App.css with theme classes**

Rewrite `frontend/src/App.css`:
```css
/* Layout */
.app-shell {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.app-body {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md) var(--space-lg);
}

/* TopNav */
.topnav {
  display: flex;
  align-items: center;
  height: var(--topnav-height);
  background: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
  padding: 0 var(--space-lg);
  flex-shrink: 0;
  gap: var(--space-md);
}

.topnav-logo {
  font-weight: 700;
  font-size: 14px;
  color: var(--color-accent);
  letter-spacing: 0.5px;
  white-space: nowrap;
}

.topnav-sections {
  display: flex;
  gap: 0;
  background: var(--color-bg-primary);
  border-radius: var(--radius-sm);
  padding: 2px;
  margin-left: var(--space-lg);
}

.topnav-section {
  padding: 5px 12px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  color: var(--color-text-muted);
  cursor: pointer;
  border: none;
  background: none;
  transition: all 0.15s;
}

.topnav-section:hover {
  color: var(--color-text-secondary);
}

.topnav-section.active {
  background: var(--color-accent-bg);
  color: var(--color-accent);
}

.topnav-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: var(--space-md);
  font-size: 11px;
  color: var(--color-text-secondary);
}

.topnav-status-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--color-critical);
}

.topnav-status-dot.connected {
  background: var(--color-healthy);
  box-shadow: 0 0 5px var(--color-healthy);
}

.topnav-badge {
  background: var(--color-bg-tertiary);
  padding: 2px 10px;
  border-radius: 10px;
  font-size: 10px;
}

/* Sidebar */
.sidebar {
  width: var(--sidebar-width);
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border);
  padding: var(--space-sm) 6px;
  flex-shrink: 0;
  overflow-y: auto;
}

.sidebar-section-title {
  color: var(--color-text-muted);
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
  padding: 0 6px;
}

.sidebar-item {
  display: block;
  width: 100%;
  padding: 5px 8px;
  color: var(--color-text-muted);
  font-size: 10px;
  cursor: pointer;
  border: none;
  background: none;
  text-align: left;
  border-radius: var(--radius-sm);
  margin-bottom: 2px;
  transition: all 0.15s;
}

.sidebar-item:hover {
  color: var(--color-text-secondary);
  background: var(--color-bg-tertiary);
}

.sidebar-item.active {
  color: var(--color-accent);
  background: var(--color-accent-bg);
  border-left: 2px solid var(--color-accent);
}

/* StatCard */
.stat-card {
  flex: 1;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: 10px 12px;
  border-top: 2px solid var(--color-border);
}

.stat-card-label {
  color: var(--color-text-muted);
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-card-value {
  color: var(--color-text-primary);
  font-size: 22px;
  font-weight: 700;
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.stat-card-delta {
  font-size: 10px;
  font-weight: 400;
}

.stat-card-delta.positive { color: var(--color-healthy); }
.stat-card-delta.negative { color: var(--color-critical); }

/* StatusBadge */
.status-badge {
  font-size: 8px;
  font-weight: 600;
  text-transform: uppercase;
  padding: 1px 7px;
  border-radius: 10px;
  display: inline-block;
}

.status-badge.critical {
  background: var(--color-critical-bg);
  color: var(--color-critical-text);
}

.status-badge.warning {
  background: var(--color-warning-bg);
  color: var(--color-warning-text);
}

.status-badge.info {
  background: var(--color-info-bg);
  color: var(--color-info-text);
}

.status-badge.healthy {
  background: var(--color-healthy-bg);
  color: var(--color-healthy-text);
}

/* SeverityDot */
.severity-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
  flex-shrink: 0;
}

.severity-dot.critical { background: var(--color-critical); }
.severity-dot.warning { background: var(--color-warning); }
.severity-dot.info { background: var(--color-info); }
.severity-dot.healthy { background: var(--color-healthy); }

/* FilterTabs */
.filter-tabs {
  display: flex;
  gap: 2px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: 2px;
}

.filter-tab {
  padding: 4px 10px;
  border-radius: var(--radius-sm);
  font-size: 10px;
  color: var(--color-text-muted);
  cursor: pointer;
  border: none;
  background: none;
  transition: all 0.15s;
}

.filter-tab:hover {
  color: var(--color-text-secondary);
}

.filter-tab.active {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

/* DataTable */
.data-table {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.data-table-header {
  display: flex;
  background: var(--color-bg-tertiary);
  padding: 6px var(--space-md);
  color: var(--color-text-secondary);
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.data-table-row {
  display: flex;
  padding: 7px var(--space-md);
  border-bottom: 1px solid var(--color-bg-primary);
  font-size: 10px;
  color: var(--color-text-primary);
  align-items: center;
  cursor: pointer;
  transition: background 0.1s;
}

.data-table-row:hover {
  background: rgba(255,255,255,0.02);
}

.data-table-row:last-child {
  border-bottom: none;
}

/* EmptyState */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--color-text-disabled);
  font-size: 13px;
  text-align: center;
}

.empty-state-icon {
  font-size: 32px;
  margin-bottom: var(--space-sm);
  opacity: 0.3;
}

/* TimeSeriesChart */
.chart-container {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--space-md);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-sm);
}

.chart-title {
  color: var(--color-text-secondary);
  font-size: 11px;
  font-weight: 500;
}

.chart-legend {
  display: flex;
  gap: var(--space-sm);
  font-size: 9px;
  color: var(--color-text-muted);
}

.chart-legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  cursor: pointer;
}

/* SensorCard (mini) */
.sensor-mini-card {
  flex: 1;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: 10px;
  border-top: 2px solid var(--color-border);
}

.sensor-mini-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.sensor-mini-card-name {
  color: var(--color-text-primary);
  font-size: 11px;
  font-weight: 500;
}

.sensor-mini-card-type {
  color: var(--color-text-muted);
  font-size: 9px;
}

.sensor-mini-card-value {
  font-size: 20px;
  font-weight: 700;
  color: var(--color-text-primary);
  margin-bottom: 2px;
}

.sensor-mini-card-chart {
  height: 24px;
  margin-top: 4px;
}

/* TimeRangeSelector */
.time-range-selector {
  display: flex;
  gap: 2px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: 2px;
}

.time-range-btn {
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  font-size: 10px;
  color: var(--color-text-muted);
  cursor: pointer;
  border: none;
  background: none;
  transition: all 0.15s;
}

.time-range-btn.active {
  background: var(--color-bg-tertiary);
  color: var(--color-text-primary);
}

/* SearchBar */
.search-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
  padding: 5px 10px;
  border: 1px solid var(--color-border);
  flex: 2;
}

.search-bar input {
  background: none;
  border: none;
  color: var(--color-text-primary);
  font-size: 11px;
  outline: none;
  width: 100%;
}

.search-bar input::placeholder {
  color: var(--color-text-disabled);
}

/* Evidence panel */
.evidence-panel {
  background: var(--color-bg-input);
  border-radius: var(--radius-sm);
  padding: 10px;
}

.evidence-panel-title {
  color: var(--color-text-muted);
  font-size: 9px;
  text-transform: uppercase;
  margin-bottom: 6px;
}

.evidence-grid {
  display: flex;
  gap: var(--space-md);
  flex-wrap: wrap;
}

.evidence-item-label {
  color: var(--color-text-muted);
  font-size: 9px;
}

.evidence-item-value {
  color: var(--color-text-primary);
  font-size: 12px;
  font-weight: 600;
}

/* Feedback buttons */
.feedback-confirm {
  flex: 1;
  padding: 8px;
  background: var(--color-healthy-bg);
  color: var(--color-healthy-text);
  border: 1px solid var(--color-healthy);
  border-radius: var(--radius-md);
  font-size: 11px;
  cursor: pointer;
}

.feedback-reject {
  flex: 1;
  padding: 8px;
  background: var(--color-critical-bg);
  color: var(--color-critical-text);
  border: 1px solid var(--color-critical);
  border-radius: var(--radius-md);
  font-size: 11px;
  cursor: pointer;
}

/* Section card */
.section-card {
  background: var(--color-bg-secondary);
  border-radius: var(--radius-md);
  padding: var(--space-md);
  margin-bottom: var(--space-sm);
}

.section-card-title {
  color: var(--color-text-muted);
  font-size: 9px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-sm);
}

/* Input & form */
.form-input {
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 4px 8px;
  color: var(--color-text-primary);
  font-size: 10px;
  width: 100%;
}

.form-input:focus {
  outline: none;
  border-color: var(--color-accent);
}

.form-label {
  color: var(--color-text-disabled);
  font-size: 9px;
  margin-bottom: 2px;
}

.btn-primary {
  padding: 4px 12px;
  background: var(--color-accent-bg);
  color: var(--color-accent);
  border: 1px solid var(--color-accent);
  border-radius: var(--radius-sm);
  font-size: 10px;
  cursor: pointer;
}

.btn-primary:hover {
  background: rgba(56,189,248,0.2);
}

/* Progress bar */
.progress-bar {
  height: 4px;
  background: var(--color-bg-tertiary);
  border-radius: 2px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  border-radius: 2px;
  transition: width 0.3s;
}

/* Donut placeholder */
.donut-chart {
  width: 60px;
  height: 60px;
  border-radius: 50%;
}

/* Config row */
.config-row {
  display: flex;
  gap: var(--space-md);
}

.config-field {
  flex: 1;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 10px 16px;
  font-size: 12px;
  color: var(--color-text-primary);
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0,0,0,0.4);
}

.toast.error {
  border-color: var(--color-critical);
}

.toast.success {
  border-color: var(--color-healthy);
}
```

- [ ] **Step 3: Update main.tsx to import index.css**

Edit `frontend/src/main.tsx`:
```typescript
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App.tsx'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- [ ] **Step 4: Verify the app still compiles**

```bash
cd frontend && npx tsc -b --noEmit 2>&1 | head -20
```
Expected: no errors

- [ ] **Step 5: Commit**

```bash
git add frontend/src/index.css frontend/src/App.css frontend/src/main.tsx
git commit -m "style: add CSS theme system with variables and component classes"
```

---

### Task 3: Reusable components — StatCard, StatusBadge, SeverityDot, MiniSparkline

**Files:**
- Create: `frontend/src/components/StatCard.tsx`
- Create: `frontend/src/components/StatusBadge.tsx`
- Create: `frontend/src/components/SeverityDot.tsx`
- Create: `frontend/src/components/MiniSparkline.tsx`
- Test: `frontend/src/components/__tests__/StatCard.test.tsx`
- Test: `frontend/src/components/__tests__/StatusBadge.test.tsx`
- Test: `frontend/src/components/__tests__/SeverityDot.test.tsx`
- Test: `frontend/src/components/__tests__/MiniSparkline.test.tsx`

- [ ] **Step 1: Write StatCard component**

Create `frontend/src/components/StatCard.tsx`:
```typescript
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
      {sparklineData && (
        <MiniSparkline data={sparklineData} color={accentColor} height={16} />
      )}
    </div>
  )
}

import MiniSparkline from './MiniSparkline'
```

Wait, the import should be at the top. Let me fix this — write the file with the import at the top:

Actually let me restructure. MiniSparkline needs to be created first since StatCard uses it.

Let me reorder: create MiniSparkline first, then StatusBadge, SeverityDot (these have no dependencies), then StatCard (depends on MiniSparkline).

- [ ] **Step 1: Write MiniSparkline component**

Create `frontend/src/components/MiniSparkline.tsx`:
```typescript
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
```

- [ ] **Step 2: Write MiniSparkline test**

Create `frontend/src/components/__tests__/MiniSparkline.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import MiniSparkline from '../MiniSparkline'

describe('MiniSparkline', () => {
  it('renders an svg', () => {
    const { container } = render(<MiniSparkline data={[1, 2, 3, 4, 5]} />)
    expect(container.querySelector('svg')).toBeInTheDocument()
  })

  it('renders a path element', () => {
    const { container } = render(<MiniSparkline data={[1, 2, 3]} />)
    expect(container.querySelector('path')).toBeInTheDocument()
  })

  it('renders nothing when data has less than 2 points', () => {
    const { container } = render(<MiniSparkline data={[1]} />)
    expect(container.querySelector('path')?.getAttribute('d')).toBe('')
  })
})
```

- [ ] **Step 3: Run MiniSparkline tests**

```bash
cd frontend && npx vitest run src/components/__tests__/MiniSparkline.test.tsx
```
Expected: 3 tests pass

- [ ] **Step 4: Write StatusBadge component**

Create `frontend/src/components/StatusBadge.tsx`:
```typescript
type BadgeVariant = 'critical' | 'warning' | 'info' | 'healthy'

interface StatusBadgeProps {
  variant: BadgeVariant
  label: string
}

export default function StatusBadge({ variant, label }: StatusBadgeProps) {
  return <span className={`status-badge ${variant}`}>{label}</span>
}
```

- [ ] **Step 5: Write StatusBadge test**

Create `frontend/src/components/__tests__/StatusBadge.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatusBadge from '../StatusBadge'

describe('StatusBadge', () => {
  it('renders the label', () => {
    render(<StatusBadge variant="critical" label="CRIT" />)
    expect(screen.getByText('CRIT')).toBeInTheDocument()
  })

  it('applies variant class', () => {
    const { container } = render(<StatusBadge variant="warning" label="WARN" />)
    expect(container.firstChild).toHaveClass('status-badge')
    expect(container.firstChild).toHaveClass('warning')
  })
})
```

- [ ] **Step 6: Run StatusBadge test**

```bash
cd frontend && npx vitest run src/components/__tests__/StatusBadge.test.tsx
```
Expected: 2 tests pass

- [ ] **Step 7: Write SeverityDot component**

Create `frontend/src/components/SeverityDot.tsx`:
```typescript
type Severity = 'critical' | 'warning' | 'info' | 'healthy'

interface SeverityDotProps {
  severity: Severity
}

export default function SeverityDot({ severity }: SeverityDotProps) {
  return <span className={`severity-dot ${severity}`} />
}
```

- [ ] **Step 8: Write SeverityDot test**

Create `frontend/src/components/__tests__/SeverityDot.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import SeverityDot from '../SeverityDot'

describe('SeverityDot', () => {
  it('applies severity class', () => {
    const { container } = render(<SeverityDot severity="critical" />)
    expect(container.firstChild).toHaveClass('severity-dot')
    expect(container.firstChild).toHaveClass('critical')
  })
})
```

- [ ] **Step 9: Write StatCard component (updated — import at top)**

Create `frontend/src/components/StatCard.tsx`:
```typescript
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
```

- [ ] **Step 10: Write StatCard test**

Create `frontend/src/components/__tests__/StatCard.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import StatCard from '../StatCard'

describe('StatCard', () => {
  it('renders label and value', () => {
    render(<StatCard label="Critical" value={3} />)
    expect(screen.getByText('Critical')).toBeInTheDocument()
    expect(screen.getByText('3')).toBeInTheDocument()
  })

  it('renders delta when provided', () => {
    render(<StatCard label="Warning" value={12} delta="+2" deltaPositive={false} />)
    expect(screen.getByText('+2')).toBeInTheDocument()
    expect(screen.getByText('+2')).toHaveClass('negative')
  })

  it('applies accent color as border-top', () => {
    const { container } = render(<StatCard label="Test" value={1} accentColor="#ef4444" />)
    expect(container.firstChild).toHaveStyle({ borderTopColor: '#ef4444' })
  })
})
```

- [ ] **Step 11: Run all component tests**

```bash
cd frontend && npx vitest run src/components/__tests__/
```
Expected: all tests pass

- [ ] **Step 12: Commit**

```bash
git add frontend/src/components/StatCard.tsx frontend/src/components/StatusBadge.tsx frontend/src/components/SeverityDot.tsx frontend/src/components/MiniSparkline.tsx frontend/src/components/__tests__/
git commit -m "feat: add StatCard, StatusBadge, SeverityDot, and MiniSparkline components"
```

---

### Task 4: Reusable components — FilterTabs, EmptyState, DataTable

**Files:**
- Create: `frontend/src/components/FilterTabs.tsx`
- Create: `frontend/src/components/EmptyState.tsx`
- Create: `frontend/src/components/DataTable.tsx`
- Test: `frontend/src/components/__tests__/FilterTabs.test.tsx`
- Test: `frontend/src/components/__tests__/EmptyState.test.tsx`
- Test: `frontend/src/components/__tests__/DataTable.test.tsx`

- [ ] **Step 1: Write FilterTabs component**

Create `frontend/src/components/FilterTabs.tsx`:
```typescript
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
```

- [ ] **Step 2: Write FilterTabs test**

Create `frontend/src/components/__tests__/FilterTabs.test.tsx`:
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import FilterTabs from '../FilterTabs'

describe('FilterTabs', () => {
  const options = [
    { key: 'all', label: 'All' },
    { key: 'critical', label: 'Critical' },
  ]

  it('renders all options', () => {
    render(<FilterTabs options={options} selected="all" onChange={() => {}} />)
    expect(screen.getByText('All')).toBeInTheDocument()
    expect(screen.getByText('Critical')).toBeInTheDocument()
  })

  it('marks selected option as active', () => {
    render(<FilterTabs options={options} selected="critical" onChange={() => {}} />)
    expect(screen.getByText('Critical')).toHaveClass('active')
  })

  it('calls onChange when clicked', async () => {
    const onChange = vi.fn()
    render(<FilterTabs options={options} selected="all" onChange={onChange} />)
    await userEvent.click(screen.getByText('Critical'))
    expect(onChange).toHaveBeenCalledWith('critical')
  })
})
```

- [ ] **Step 3: Run FilterTabs test**

```bash
cd frontend && npx vitest run src/components/__tests__/FilterTabs.test.tsx
```
Expected: 3 tests pass

- [ ] **Step 4: Write EmptyState component**

Create `frontend/src/components/EmptyState.tsx`:
```typescript
interface EmptyStateProps {
  icon?: string
  message: string
}

export default function EmptyState({ icon = '—', message }: EmptyStateProps) {
  return (
    <div className="empty-state">
      <div className="empty-state-icon">{icon}</div>
      <p>{message}</p>
    </div>
  )
}
```

- [ ] **Step 5: Write EmptyState test**

Create `frontend/src/components/__tests__/EmptyState.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import EmptyState from '../EmptyState'

describe('EmptyState', () => {
  it('renders the message', () => {
    render(<EmptyState message="No data yet" />)
    expect(screen.getByText('No data yet')).toBeInTheDocument()
  })

  it('renders default icon', () => {
    render(<EmptyState message="Empty" />)
    expect(screen.getByText('—')).toBeInTheDocument()
  })
})
```

- [ ] **Step 6: Write DataTable component**

Create `frontend/src/components/DataTable.tsx`:
```typescript
import type { ReactNode } from 'react'

interface Column {
  key: string
  label: string
  flex: number
  render?: (row: Record<string, unknown>) => ReactNode
}

interface DataTableProps {
  columns: Column[]
  rows: Record<string, unknown>[]
  onRowClick?: (row: Record<string, unknown>) => void
  rowKey: (row: Record<string, unknown>) => string
}

export default function DataTable({ columns, rows, onRowClick, rowKey }: DataTableProps) {
  return (
    <div className="data-table">
      <div className="data-table-header">
        {columns.map(col => (
          <span key={col.key} style={{ flex: col.flex }}>{col.label}</span>
        ))}
      </div>
      {rows.map(row => (
        <div
          key={rowKey(row)}
          className="data-table-row"
          onClick={() => onRowClick?.(row)}
        >
          {columns.map(col => (
            <span key={col.key} style={{ flex: col.flex }}>
              {col.render ? col.render(row) : String(row[col.key] ?? '')}
            </span>
          ))}
        </div>
      ))}
    </div>
  )
}
```

- [ ] **Step 7: Write DataTable test**

Create `frontend/src/components/__tests__/DataTable.test.tsx`:
```typescript
import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import DataTable from '../DataTable'

const columns = [
  { key: 'name', label: 'Name', flex: 1 },
  { key: 'status', label: 'Status', flex: 1 },
]

const rows = [
  { name: 'pump-001', status: 'OK' },
  { name: 'pump-002', status: 'WARN' },
]

describe('DataTable', () => {
  it('renders header labels', () => {
    render(<DataTable columns={columns} rows={rows} rowKey={r => String(r.name)} />)
    expect(screen.getByText('Name')).toBeInTheDocument()
    expect(screen.getByText('Status')).toBeInTheDocument()
  })

  it('renders row data', () => {
    render(<DataTable columns={columns} rows={rows} rowKey={r => String(r.name)} />)
    expect(screen.getByText('pump-001')).toBeInTheDocument()
    expect(screen.getByText('OK')).toBeInTheDocument()
  })

  it('calls onRowClick when a row is clicked', async () => {
    const onClick = vi.fn()
    render(<DataTable columns={columns} rows={rows} onRowClick={onClick} rowKey={r => String(r.name)} />)
    await userEvent.click(screen.getByText('pump-001'))
    expect(onClick).toHaveBeenCalledWith(rows[0])
  })
})
```

- [ ] **Step 8: Run all component tests**

```bash
cd frontend && npx vitest run src/components/__tests__/
```
Expected: all tests pass

- [ ] **Step 9: Commit**

```bash
git add frontend/src/components/FilterTabs.tsx frontend/src/components/EmptyState.tsx frontend/src/components/DataTable.tsx frontend/src/components/__tests__/
git commit -m "feat: add FilterTabs, EmptyState, and DataTable components"
```

---

### Task 5: TimeSeriesChart component

**Files:**
- Create: `frontend/src/components/TimeSeriesChart.tsx`
- Test: `frontend/src/components/__tests__/TimeSeriesChart.test.tsx`

- [ ] **Step 1: Write TimeSeriesChart component**

Create `frontend/src/components/TimeSeriesChart.tsx`:
```typescript
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
        data: [],
        markArea: {
          silent: true,
          itemStyle: { color: 'rgba(239,68,68,0.06)' },
          data: [[{ xAxis: w.start }, { xAxis: w.end }]],
        },
        showInLegend: false,
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
      ...(anomalyPoints?.map(p => ({
        type: 'scatter' as const,
        name: 'anomaly',
        data: [[p.time, p.value]],
        symbolSize: 8,
        itemStyle: { color: '#ef4444', borderColor: '#0f172a', borderWidth: 2 },
        showInLegend: false,
      })) || []),
    ],
  }

  return (
    <div className="chart-container">
      {title && <div className="chart-title">{title}</div>}
      <ReactECharts option={option} style={{ height }} />
    </div>
  )
}

export { SENSOR_COLORS }
```

- [ ] **Step 2: Write TimeSeriesChart test**

Create `frontend/src/components/__tests__/TimeSeriesChart.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render } from '@testing-library/react'
import TimeSeriesChart from '../TimeSeriesChart'

describe('TimeSeriesChart', () => {
  const mockSeries = [{
    name: 'temp-01',
    color: '#f97316',
    data: [['2026-05-25T10:00:00Z', 25.0], ['2026-05-25T10:01:00Z', 26.0]] as [string, number][],
  }]

  it('renders chart container', () => {
    const { container } = render(<TimeSeriesChart series={mockSeries} />)
    expect(container.querySelector('.chart-container')).toBeInTheDocument()
  })

  it('renders title when provided', () => {
    render(<TimeSeriesChart series={mockSeries} title="Temperature" />)
    expect(document.body.textContent).toContain('Temperature')
  })

  it('renders with anomaly windows', () => {
    const { container } = render(
      <TimeSeriesChart
        series={mockSeries}
        anomalyWindows={[{ start: '2026-05-25T10:00:30Z', end: '2026-05-25T10:00:45Z' }]}
      />
    )
    expect(container.querySelector('.chart-container')).toBeInTheDocument()
  })

  it('renders with anomaly points', () => {
    const { container } = render(
      <TimeSeriesChart
        series={mockSeries}
        anomalyPoints={[{ time: '2026-05-25T10:00:30Z', value: 85.0 }]}
      />
    )
    expect(container.querySelector('.chart-container')).toBeInTheDocument()
  })
})
```

- [ ] **Step 3: Run TimeSeriesChart test**

```bash
cd frontend && npx vitest run src/components/__tests__/TimeSeriesChart.test.tsx
```
Expected: 4 tests pass

- [ ] **Step 4: Commit**

```bash
git add frontend/src/components/TimeSeriesChart.tsx frontend/src/components/__tests__/TimeSeriesChart.test.tsx
git commit -m "feat: add TimeSeriesChart component with anomaly overlay support"
```

---

### Task 6: Custom hooks — usePolling and useChartData

**Files:**
- Create: `frontend/src/hooks/usePolling.ts`
- Create: `frontend/src/hooks/useChartData.ts`
- Test: `frontend/src/hooks/__tests__/usePolling.test.ts`
- Test: `frontend/src/hooks/__tests__/useChartData.test.ts`

- [ ] **Step 1: Write usePolling hook**

Create `frontend/src/hooks/usePolling.ts`:
```typescript
import { useEffect, useRef } from 'react'

export function usePolling(callback: () => void, intervalMs: number, enabled: boolean = true) {
  const savedCallback = useRef(callback)

  useEffect(() => {
    savedCallback.current = callback
  }, [callback])

  useEffect(() => {
    if (!enabled) return
    savedCallback.current()
    const id = setInterval(() => savedCallback.current(), intervalMs)
    return () => clearInterval(id)
  }, [intervalMs, enabled])
}
```

- [ ] **Step 2: Write usePolling test**

Create `frontend/src/hooks/__tests__/usePolling.test.ts`:
```typescript
import { describe, it, expect, vi } from 'vitest'
import { renderHook } from '@testing-library/react'
import { usePolling } from '../usePolling'

describe('usePolling', () => {
  it('calls callback immediately', () => {
    const cb = vi.fn()
    renderHook(() => usePolling(cb, 5000))
    expect(cb).toHaveBeenCalledTimes(1)
  })

  it('does not call when disabled', () => {
    const cb = vi.fn()
    renderHook(() => usePolling(cb, 5000, false))
    expect(cb).not.toHaveBeenCalled()
  })
})
```

- [ ] **Step 3: Run usePolling test**

```bash
cd frontend && npx vitest run src/hooks/__tests__/usePolling.test.ts
```
Expected: 2 tests pass

- [ ] **Step 4: Write useChartData hook**

Create `frontend/src/hooks/useChartData.ts`:
```typescript
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
```

- [ ] **Step 5: Write useChartData test**

Create `frontend/src/hooks/__tests__/useChartData.test.ts`:
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'

vi.mock('../../api', () => ({
  fetchSensorHistory: vi.fn().mockResolvedValue({
    data: [{ timestamp: '2026-05-25T10:00:00Z', value: 25.0 }],
  }),
}))

import { useChartData } from '../useChartData'

describe('useChartData', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('returns empty data when deviceId is empty', () => {
    const { result } = renderHook(() => useChartData('', ''))
    expect(result.current.data).toEqual([])
  })

  it('fetches data when device and sensor are provided', async () => {
    const { result } = renderHook(() => useChartData('pump-001', 'temp-01'))
    await waitFor(() => {
      expect(result.current.data.length).toBeGreaterThan(0)
    })
  })
})
```

- [ ] **Step 6: Run all hook tests**

```bash
cd frontend && npx vitest run src/hooks/__tests__/
```
Expected: 4 tests pass

- [ ] **Step 7: Commit**

```bash
git add frontend/src/hooks/ frontend/src/hooks/__tests__/
git commit -m "feat: add usePolling and useChartData custom hooks"
```

---

### Task 7: Layout shell — TopNav + Sidebar + Router in App.tsx

**Files:**
- Rewrite: `frontend/src/App.tsx`
- Create: `frontend/src/components/TopNav.tsx`
- Create: `frontend/src/components/Sidebar.tsx`
- Test: `frontend/src/components/__tests__/TopNav.test.tsx`
- Test: `frontend/src/components/__tests__/Sidebar.test.tsx`

- [ ] **Step 1: Write TopNav component**

Create `frontend/src/components/TopNav.tsx`:
```typescript
import { useNavigate, useLocation } from 'react-router-dom'

interface Section {
  key: string
  label: string
  color: string
}

const SECTIONS: Section[] = [
  { key: 'overview', label: 'Overview', color: '#38bdf8' },
  { key: 'devices', label: 'Devices', color: '#f97316' },
  { key: 'alerts', label: 'Alerts', color: '#ef4444' },
  { key: 'training', label: 'Training', color: '#8b5cf6' },
  { key: 'settings', label: 'Settings', color: '#38bdf8' },
]

interface TopNavProps {
  wsConnected: boolean
  alertCount: number
  deviceCount: number
}

export default function TopNav({ wsConnected, alertCount, deviceCount }: TopNavProps) {
  const navigate = useNavigate()
  const location = useLocation()
  const activeSection = location.pathname.split('/')[1] || 'overview'

  return (
    <header className="topnav">
      <span className="topnav-logo">IoT Sentinel</span>
      <div className="topnav-sections">
        {SECTIONS.map(s => (
          <button
            key={s.key}
            className={`topnav-section ${activeSection === s.key ? 'active' : ''}`}
            onClick={() => navigate(`/${s.key === 'overview' ? '' : s.key}`)}
            style={activeSection === s.key ? { color: s.color } : undefined}
          >
            {s.label}
          </button>
        ))}
      </div>
      <div className="topnav-right">
        <span className={`topnav-status-dot ${wsConnected ? 'connected' : ''}`} />
        <span>{wsConnected ? 'Live' : 'Disconnected'}</span>
        <span className="topnav-badge">Alerts: {alertCount}</span>
        <span className="topnav-badge">Devices: {deviceCount}</span>
      </div>
    </header>
  )
}

export { SECTIONS }
```

- [ ] **Step 2: Write TopNav test**

Create `frontend/src/components/__tests__/TopNav.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import TopNav from '../TopNav'

describe('TopNav', () => {
  it('renders all section buttons', () => {
    render(
      <MemoryRouter>
        <TopNav wsConnected={true} alertCount={5} deviceCount={3} />
      </MemoryRouter>
    )
    expect(screen.getByText('Overview')).toBeInTheDocument()
    expect(screen.getByText('Devices')).toBeInTheDocument()
    expect(screen.getByText('Alerts')).toBeInTheDocument()
  })

  it('shows connected status', () => {
    render(
      <MemoryRouter>
        <TopNav wsConnected={true} alertCount={0} deviceCount={0} />
      </MemoryRouter>
    )
    expect(screen.getByText('Live')).toBeInTheDocument()
  })

  it('shows disconnected status', () => {
    render(
      <MemoryRouter>
        <TopNav wsConnected={false} alertCount={0} deviceCount={0} />
      </MemoryRouter>
    )
    expect(screen.getByText('Disconnected')).toBeInTheDocument()
  })
})
```

- [ ] **Step 3: Run TopNav test**

```bash
cd frontend && npx vitest run src/components/__tests__/TopNav.test.tsx
```
Expected: 3 tests pass

- [ ] **Step 4: Write Sidebar component**

Create `frontend/src/components/Sidebar.tsx`:
```typescript
import { useNavigate, useLocation } from 'react-router-dom'

interface SidebarItem {
  key: string
  label: string
}

interface SidebarSection {
  title: string
  items: SidebarItem[]
  parentRoute: string
}

const SIDEBAR_MAP: Record<string, SidebarSection> = {
  overview: {
    title: 'Overview',
    parentRoute: '/',
    items: [
      { key: '', label: 'Dashboard' },
      { key: 'health', label: 'Health Map' },
      { key: 'analytics', label: 'Analytics' },
    ],
  },
  devices: {
    title: 'Devices',
    parentRoute: '/devices',
    items: [
      { key: '', label: 'Device List' },
      { key: 'sensors', label: 'Sensor Config' },
      { key: 'explorer', label: 'Data Explorer' },
    ],
  },
  alerts: {
    title: 'Alerts',
    parentRoute: '/alerts',
    items: [
      { key: '', label: 'Alert Feed' },
      { key: 'feedback', label: 'Feedback Queue' },
    ],
  },
  training: {
    title: 'Training',
    parentRoute: '/training',
    items: [
      { key: '', label: 'Model Status' },
      { key: 'drift', label: 'Drift Monitor' },
    ],
  },
  settings: {
    title: 'Settings',
    parentRoute: '/settings',
    items: [
      { key: '', label: 'Notifications' },
      { key: 'global', label: 'Global Config' },
    ],
  },
}

export default function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  const sectionKey = location.pathname.split('/')[1] || 'overview'
  const subPath = location.pathname.split('/')[2] || ''
  const section = SIDEBAR_MAP[sectionKey] || SIDEBAR_MAP.overview

  return (
    <aside className="sidebar">
      <div className="sidebar-section-title">{section.title}</div>
      {section.items.map(item => (
        <button
          key={item.key}
          className={`sidebar-item ${subPath === item.key ? 'active' : ''}`}
          onClick={() => {
            const path = item.key
              ? `${section.parentRoute}/${item.key}`
              : section.parentRoute || '/'
            navigate(path)
          }}
        >
          {item.label}
        </button>
      ))}
    </aside>
  )
}

export { SIDEBAR_MAP }
```

- [ ] **Step 5: Write Sidebar test**

Create `frontend/src/components/__tests__/Sidebar.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import Sidebar from '../Sidebar'

describe('Sidebar', () => {
  it('renders items for current section', () => {
    render(
      <MemoryRouter initialEntries={['/alerts']}>
        <Sidebar />
      </MemoryRouter>
    )
    expect(screen.getByText('Alert Feed')).toBeInTheDocument()
    expect(screen.getByText('Feedback Queue')).toBeInTheDocument()
  })
})
```

- [ ] **Step 6: Run Sidebar test**

```bash
cd frontend && npx vitest run src/components/__tests__/Sidebar.test.tsx
```
Expected: 1 test passes

- [ ] **Step 7: Rewrite App.tsx with router and layout shell**

Rewrite `frontend/src/App.tsx`:
```typescript
import { useState, useCallback, useEffect } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import TopNav from './components/TopNav'
import Sidebar from './components/Sidebar'
import OverviewPage from './pages/OverviewPage'
import DevicesPage from './pages/DevicesPage'
import DeviceDetail from './pages/DeviceDetail'
import AlertsPage from './pages/AlertsPage'
import AlertDetail from './pages/AlertDetail'
import TrainingPage from './pages/TrainingPage'
import SettingsPage from './pages/SettingsPage'
import { fetchAlerts, fetchDevices, type AlertEvent, type Device } from './api'
import { useWebSocket } from './useWebSocket'
import './App.css'

function App() {
  const [alerts, setAlerts] = useState<AlertEvent[]>([])
  const [devices, setDevices] = useState<Device[]>([])

  const onAlert = useCallback((a: AlertEvent) => {
    setAlerts(prev => [a, ...prev].slice(0, 200))
  }, [])
  const wsConnected = useWebSocket(onAlert)

  useEffect(() => {
    fetchAlerts().then(r => setAlerts(r.items))
    fetchDevices().then(r => setDevices(r.items))
  }, [])

  useEffect(() => {
    const i = setInterval(() => fetchDevices().then(r => setDevices(r.items)), 5000)
    return () => clearInterval(i)
  }, [])

  return (
    <BrowserRouter>
      <div className="app-shell">
        <TopNav
          wsConnected={wsConnected}
          alertCount={alerts.length}
          deviceCount={devices.length}
        />
        <div className="app-body">
          <Sidebar />
          <main className="main-content">
            <Routes>
              <Route path="/" element={<OverviewPage alerts={alerts} devices={devices} />} />
              <Route path="/overview" element={<Navigate to="/" replace />} />
              <Route path="/devices" element={<DevicesPage />} />
              <Route path="/devices/:deviceId" element={<DeviceDetail />} />
              <Route path="/alerts" element={<AlertsPage alerts={alerts} />} />
              <Route path="/alerts/:eventId" element={<AlertDetail alerts={alerts} />} />
              <Route path="/training" element={<TrainingPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
```

Note: the page component imports will fail until we create them. The app won't compile yet — that's expected.

- [ ] **Step 8: Commit**

```bash
git add frontend/src/App.tsx frontend/src/components/TopNav.tsx frontend/src/components/Sidebar.tsx frontend/src/components/__tests__/
git commit -m "feat: add layout shell with TopNav, Sidebar, and react-router routing"
```

---

### Task 8: OverviewPage

**Files:**
- Create: `frontend/src/pages/OverviewPage.tsx`
- Test: `frontend/src/pages/__tests__/OverviewPage.test.tsx`
- Modify: `frontend/src/api.ts` (extend types if needed)

- [ ] **Step 1: Write OverviewPage**

Create `frontend/src/pages/OverviewPage.tsx`:
```typescript
import { useState, useMemo } from 'react'
import StatCard from '../components/StatCard'
import TimeSeriesChart from '../components/TimeSeriesChart'
import SeverityDot from '../components/SeverityDot'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'
import { useChartData } from '../hooks/useChartData'
import type { AlertEvent, Device } from '../api'

interface OverviewPageProps {
  alerts: AlertEvent[]
  devices: Device[]
}

export default function OverviewPage({ alerts, devices }: OverviewPageProps) {
  const [timeRange, setTimeRange] = useState<'1h' | '6h' | '24h' | '7d'>('1h')
  const lookbackMs = { '1h': 3600000, '6h': 21600000, '24h': 86400000, '7d': 604800000 }[timeRange]

  // Pick first device with data as default chart
  const defaultDevice = devices[0]?.device_id || ''
  const defaultSensor = 'temp-01'
  const { data: chartData } = useChartData(defaultDevice, defaultSensor, lookbackMs)

  const criticalCount = alerts.filter(a => a.severity === 'critical').length
  const warningCount = alerts.filter(a => a.severity === 'warning').length
  const healthyCount = devices.length - criticalCount - warningCount

  const seriesData = useMemo(() => {
    return [{
      name: defaultSensor,
      color: '#38bdf8',
      data: chartData.map(d => [d.timestamp, d.value] as [string, number]),
    }]
  }, [chartData])

  const recentAlerts = alerts.slice(0, 5)

  // Generate mock sparkline data from alert counts
  const sparklineMock = [2, 1, 3, 2, 5, 3, 3, 4]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <h2 style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 600 }}>Dashboard</h2>
        <div className="time-range-selector">
          {(['1h', '6h', '24h', '7d'] as const).map(r => (
            <button
              key={r}
              className={`time-range-btn ${timeRange === r ? 'active' : ''}`}
              onClick={() => setTimeRange(r)}
            >
              {r}
            </button>
          ))}
        </div>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        <StatCard label="Critical" value={criticalCount} accentColor="#ef4444" sparklineData={sparklineMock} />
        <StatCard label="Warning" value={warningCount} accentColor="#f97316" sparklineData={sparklineMock} />
        <StatCard label="Healthy" value={Math.max(0, healthyCount)} accentColor="#22c55e" />
        <StatCard label="Throughput" value="1.2k" accentColor="#38bdf8" />
      </div>

      <div style={{ marginBottom: 12 }}>
        <TimeSeriesChart series={seriesData} height={260} title="Pump Station A · Temperature" />
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <div className="section-card" style={{ flex: 1 }}>
          <div className="section-card-title">Alert Feed</div>
          {recentAlerts.length === 0 ? (
            <EmptyState message="No alerts yet" />
          ) : (
            recentAlerts.map(a => (
              <div
                key={a.event_id}
                style={{
                  display: 'flex', alignItems: 'center', gap: 8,
                  padding: '6px 8px', background: 'var(--color-bg-input)',
                  borderRadius: 3, marginBottom: 4,
                  borderLeft: `2px solid ${a.severity === 'critical' ? 'var(--color-critical)' : a.severity === 'warning' ? 'var(--color-warning)' : 'var(--color-info)'}`,
                }}
              >
                <StatusBadge
                  variant={a.severity === 'critical' ? 'critical' : a.severity === 'warning' ? 'warning' : 'info'}
                  label={a.severity.toUpperCase()}
                />
                <span style={{ fontSize: 10, color: '#e2e8f0' }}>{a.device_id} / {a.sensor_id}</span>
                <span style={{ fontSize: 10, marginLeft: 'auto', color: a.severity === 'critical' ? '#fca5a5' : '#94a3b8' }}>
                  {a.anomaly_score.toFixed(2)}
                </span>
              </div>
            ))
          )}
        </div>

        <div className="section-card" style={{ flex: 1 }}>
          <div className="section-card-title">Device Health</div>
          {devices.length === 0 ? (
            <EmptyState message="No devices registered" />
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              <div
                className="donut-chart"
                style={{
                  background: `conic-gradient(#22c55e 0deg ${(healthyCount / Math.max(devices.length, 1)) * 360}deg, #f97316 ${(healthyCount / Math.max(devices.length, 1)) * 360}deg ${((healthyCount + warningCount) / Math.max(devices.length, 1)) * 360}deg, #ef4444 ${((healthyCount + warningCount) / Math.max(devices.length, 1)) * 360}deg 360deg)`,
                }}
              />
              <div style={{ fontSize: 10 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4 }}>
                  <SeverityDot severity="healthy" /> Healthy: <strong>{healthyCount}</strong>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4, marginBottom: 4 }}>
                  <SeverityDot severity="warning" /> Warning: <strong>{warningCount}</strong>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <SeverityDot severity="critical" /> Critical: <strong>{criticalCount}</strong>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Write OverviewPage test**

Create `frontend/src/pages/__tests__/OverviewPage.test.tsx`:
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import OverviewPage from '../OverviewPage'

vi.mock('../../api', () => ({
  fetchSensorHistory: vi.fn().mockResolvedValue({ data: [] }),
}))

describe('OverviewPage', () => {
  const mockAlerts = [
    { event_id: '1', device_id: 'pump-001', sensor_id: 'temp-01', sensor_type: 'temperature',
      anomaly_score: 0.95, severity: 'critical' as const, detection_source: 'statistical',
      timestamp: '2026-05-25T10:00:00Z', evidence: {}, status: 'open' },
  ]

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders dashboard title', () => {
    render(
      <MemoryRouter>
        <OverviewPage alerts={[]} devices={[]} />
      </MemoryRouter>
    )
    expect(screen.getByText('Dashboard')).toBeInTheDocument()
  })

  it('shows alert in feed', () => {
    render(
      <MemoryRouter>
        <OverviewPage alerts={mockAlerts} devices={[]} />
      </MemoryRouter>
    )
    expect(screen.getByText('pump-001 / temp-01')).toBeInTheDocument()
  })

  it('shows empty state when no alerts', () => {
    render(
      <MemoryRouter>
        <OverviewPage alerts={[]} devices={[]} />
      </MemoryRouter>
    )
    expect(screen.getByText('No alerts yet')).toBeInTheDocument()
  })
})
```

- [ ] **Step 3: Run OverviewPage test**

```bash
cd frontend && npx vitest run src/pages/__tests__/OverviewPage.test.tsx
```
Expected: 3 tests pass

- [ ] **Step 4: Commit**

```bash
git add frontend/src/pages/OverviewPage.tsx frontend/src/pages/__tests__/OverviewPage.test.tsx
git commit -m "feat: add OverviewPage with stat cards, chart, alert feed, and health donut"
```

---

### Task 9: DevicesPage + DeviceDetail

**Files:**
- Create: `frontend/src/pages/DevicesPage.tsx`
- Create: `frontend/src/pages/DeviceDetail.tsx`
- Test: `frontend/src/pages/__tests__/DevicesPage.test.tsx`
- Test: `frontend/src/pages/__tests__/DeviceDetail.test.tsx`

- [ ] **Step 1: Write DevicesPage**

Create `frontend/src/pages/DevicesPage.tsx`:
```typescript
import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import DataTable from '../components/DataTable'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'
import { fetchDevices, type Device } from '../api'
import { usePolling } from '../hooks/usePolling'

export default function DevicesPage() {
  const [devices, setDevices] = useState<Device[]>([])
  const [search, setSearch] = useState('')
  const [typeFilter, setTypeFilter] = useState('all')
  const navigate = useNavigate()

  const loadDevices = () => {
    fetchDevices().then(r => setDevices(r.items))
  }

  useEffect(() => { loadDevices() }, [])
  usePolling(loadDevices, 5000)

  const filtered = devices.filter(d => {
    if (search && !d.device_id.toLowerCase().includes(search.toLowerCase())) return false
    return true
  })

  const columns = [
    { key: 'device_id', label: 'Device', flex: 2, render: (r: Record<string, unknown>) => (
      <span style={{ fontWeight: 500 }}>{String(r.device_id)}</span>
    )},
    { key: 'device_type', label: 'Type', flex: 1 },
    { key: 'sensors', label: 'Sensors', flex: 0.8, render: () => <span style={{ color: '#94a3b8' }}>4</span> },
    { key: 'status', label: 'Status', flex: 1, render: (r: Record<string, unknown>) => {
      const status = String(r.training_status || 'active')
      return <StatusBadge variant={status === 'active' ? 'healthy' : 'warning'} label={status} />
    }},
    { key: 'training_status', label: 'Training', flex: 1, render: (r: Record<string, unknown>) => (
      <span style={{ color: '#94a3b8' }}>{String(r.training_status || 'active')}</span>
    )},
    { key: 'arrow', label: '', flex: 0.3, render: () => <span style={{ color: '#64748b' }}>→</span> },
  ]

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12, alignItems: 'center' }}>
        <div className="search-bar">
          <span style={{ color: '#475569' }}>🔍</span>
          <input
            placeholder="Search devices..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon="📡" message={search ? 'No devices match your search' : 'No devices registered yet — ingest data via API'} />
      ) : (
        <DataTable
          columns={columns}
          rows={filtered.map(d => ({ ...d } as unknown as Record<string, unknown>))}
          onRowClick={row => navigate(`/devices/${row.device_id}`)}
          rowKey={r => String(r.device_id)}
        />
      )}
    </div>
  )
}
```

- [ ] **Step 2: Write DeviceDetail**

Create `frontend/src/pages/DeviceDetail.tsx`:
```typescript
import { useParams, useNavigate } from 'react-router-dom'
import { useMemo } from 'react'
import TimeSeriesChart from '../components/TimeSeriesChart'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'
import { useChartData } from '../hooks/useChartData'
import { SENSOR_COLORS } from '../components/TimeSeriesChart'

// Mock sensor list for display — in production this comes from device config
const MOCK_SENSORS = [
  { id: 'temp-01', type: 'temperature', value: 42.3, unit: '°C', color: '#f97316' },
  { id: 'vib-01', type: 'vibration', value: 0.8, unit: 'mm/s', color: '#e11d48' },
  { id: 'cur-01', type: 'current', value: 12.4, unit: 'A', color: '#facc15' },
  { id: 'hum-01', type: 'humidity', value: 72, unit: '%', color: '#22d3ee' },
]

export default function DeviceDetail() {
  const { deviceId } = useParams<{ deviceId: string }>()
  const navigate = useNavigate()
  const { data: chartData } = useChartData(deviceId || '', MOCK_SENSORS[0].id)

  const allSeriesData = useMemo(() => {
    return MOCK_SENSORS.map(s => ({
      name: s.id,
      color: s.color,
      data: chartData.map(d => [d.timestamp, d.value] as [string, number]),
    }))
  }, [chartData])

  if (!deviceId) return <EmptyState message="No device specified" />

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <button
          onClick={() => navigate('/devices')}
          style={{ background: 'none', border: 'none', color: '#64748b', fontSize: 11, cursor: 'pointer' }}
        >
          ← Back to Devices
        </button>
        <span style={{ color: '#334155' }}>|</span>
        <span style={{ color: '#e2e8f0', fontWeight: 600, fontSize: 12 }}>{deviceId}</span>
        <StatusBadge variant="critical" label="Critical Status" />
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        {MOCK_SENSORS.map(s => (
          <div key={s.id} className="sensor-mini-card" style={{ borderTopColor: s.color }}>
            <div className="sensor-mini-card-header">
              <span className="sensor-mini-card-name">{s.id}</span>
              <span className="sensor-mini-card-type">{s.type}</span>
            </div>
            <div className="sensor-mini-card-value">{s.value}{s.unit}</div>
          </div>
        ))}
      </div>

      <div style={{ marginBottom: 12 }}>
        <TimeSeriesChart series={allSeriesData} height={240} title="Sensor Data — All Sensors" />
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <div className="section-card" style={{ flex: 1 }}>
          <div className="section-card-title">Hard Boundary Config</div>
          <div className="config-row">
            {['Min', 'Max', 'Deadband'].map(label => (
              <div className="config-field" key={label}>
                <div className="form-label">{label}</div>
                <input className="form-input" defaultValue={label === 'Deadband' ? '±0.5°C' : label === 'Max' ? '80°C' : '0°C'} />
              </div>
            ))}
            <button className="btn-primary" style={{ alignSelf: 'flex-end' }}>Save</button>
          </div>
        </div>
        <div className="section-card" style={{ flex: 1 }}>
          <div className="section-card-title">Recent Alerts</div>
          <p style={{ fontSize: 10, color: '#94a3b8' }}>CRIT temp-01 85°C <span style={{ color: '#475569', float: 'right' }}>2m ago</span></p>
          <p style={{ fontSize: 10, color: '#94a3b8', marginTop: 4 }}>WARN cur-01 12.4A <span style={{ color: '#475569', float: 'right' }}>12m ago</span></p>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Write DevicesPage test**

Create `frontend/src/pages/__tests__/DevicesPage.test.tsx`:
```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import DevicesPage from '../DevicesPage'

vi.mock('../../api', () => ({
  fetchDevices: vi.fn().mockResolvedValue({
    items: [{ device_id: 'pump-001', device_type: 'Pump', training_status: 'active', model_version: 'v1' }],
  }),
}))

describe('DevicesPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders search bar', () => {
    render(
      <MemoryRouter>
        <DevicesPage />
      </MemoryRouter>
    )
    expect(screen.getByPlaceholderText('Search devices...')).toBeInTheDocument()
  })

  it('shows device in table after load', async () => {
    render(
      <MemoryRouter>
        <DevicesPage />
      </MemoryRouter>
    )
    expect(await screen.findByText('pump-001')).toBeInTheDocument()
  })
})
```

- [ ] **Step 4: Write DeviceDetail test**

Create `frontend/src/pages/__tests__/DeviceDetail.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Route, Routes } from 'react-router-dom'
import DeviceDetail from '../DeviceDetail'

describe('DeviceDetail', () => {
  it('renders device id from route', async () => {
    render(
      <MemoryRouter initialEntries={['/devices/pump-001']}>
        <Routes>
          <Route path="/devices/:deviceId" element={<DeviceDetail />} />
        </Routes>
      </MemoryRouter>
    )
    expect(await screen.findByText('pump-001')).toBeInTheDocument()
  })

  it('shows back button', async () => {
    render(
      <MemoryRouter initialEntries={['/devices/pump-001']}>
        <Routes>
          <Route path="/devices/:deviceId" element={<DeviceDetail />} />
        </Routes>
      </MemoryRouter>
    )
    expect(await screen.findByText('← Back to Devices')).toBeInTheDocument()
  })
})
```

- [ ] **Step 5: Run page tests**

```bash
cd frontend && npx vitest run src/pages/__tests__/DevicesPage.test.tsx src/pages/__tests__/DeviceDetail.test.tsx
```
Expected: 4 tests pass

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/DevicesPage.tsx frontend/src/pages/DeviceDetail.tsx frontend/src/pages/__tests__/DevicesPage.test.tsx frontend/src/pages/__tests__/DeviceDetail.test.tsx
git commit -m "feat: add DevicesPage with search/filter and DeviceDetail view"
```

---

### Task 10: AlertsPage + AlertDetail

**Files:**
- Create: `frontend/src/pages/AlertsPage.tsx`
- Create: `frontend/src/pages/AlertDetail.tsx`
- Test: `frontend/src/pages/__tests__/AlertsPage.test.tsx`
- Test: `frontend/src/pages/__tests__/AlertDetail.test.tsx`

- [ ] **Step 1: Write AlertsPage**

Create `frontend/src/pages/AlertsPage.tsx`:
```typescript
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DataTable from '../components/DataTable'
import FilterTabs from '../components/FilterTabs'
import SeverityDot from '../components/SeverityDot'
import StatusBadge from '../components/StatusBadge'
import EmptyState from '../components/EmptyState'
import type { AlertEvent } from '../api'

interface AlertsPageProps {
  alerts: AlertEvent[]
}

export default function AlertsPage({ alerts }: AlertsPageProps) {
  const [severityFilter, setSeverityFilter] = useState('all')
  const [statusFilter, setStatusFilter] = useState('open')
  const navigate = useNavigate()

  const filtered = alerts.filter(a => {
    if (severityFilter !== 'all' && a.severity !== severityFilter) return false
    if (statusFilter !== 'all' && a.status !== statusFilter) return false
    return true
  })

  const columns = [
    { key: 'severity', label: '', flex: 0.3, render: (r: Record<string, unknown>) => (
      <SeverityDot severity={String(r.severity) as 'critical' | 'warning' | 'info'} />
    )},
    { key: 'device_id', label: 'Device', flex: 1.2, render: (r: Record<string, unknown>) => (
      <span style={{ fontWeight: 500 }}>{String(r.device_id)}</span>
    )},
    { key: 'sensor_id', label: 'Sensor', flex: 1, render: (r: Record<string, unknown>) => (
      <span style={{ color: '#94a3b8' }}>{String(r.sensor_id)}</span>
    )},
    { key: 'detection_source', label: 'Source', flex: 0.8, render: (r: Record<string, unknown>) => (
      <span style={{ color: '#94a3b8' }}>{String(r.detection_source)}</span>
    )},
    { key: 'anomaly_score', label: 'Score', flex: 0.8, render: (r: Record<string, unknown>) => (
      <span style={{ fontFamily: 'monospace', color: Number(r.anomaly_score) > 0.8 ? '#fca5a5' : '#94a3b8' }}>
        {Number(r.anomaly_score).toFixed(2)}
      </span>
    )},
    { key: 'timestamp', label: 'Time', flex: 1, render: (r: Record<string, unknown>) => {
      const ts = new Date(String(r.timestamp))
      return <span style={{ color: '#64748b' }}>{ts.toLocaleTimeString()}</span>
    }},
    { key: 'status', label: 'Status', flex: 0.6, render: (r: Record<string, unknown>) => (
      <StatusBadge variant={String(r.status) === 'confirmed' ? 'healthy' : String(r.status) === 'rejected' ? 'info' : 'warning'} label={String(r.status)} />
    )},
    { key: 'arrow', label: '', flex: 0.3, render: () => <span style={{ color: '#64748b' }}>→</span> },
  ]

  return (
    <div>
      <div style={{ display: 'flex', gap: 8, marginBottom: 12, alignItems: 'center' }}>
        <FilterTabs
          options={[
            { key: 'all', label: 'All' },
            { key: 'critical', label: 'Critical' },
            { key: 'warning', label: 'Warning' },
            { key: 'info', label: 'Info' },
          ]}
          selected={severityFilter}
          onChange={setSeverityFilter}
        />
        <FilterTabs
          options={[
            { key: 'all', label: 'All Status' },
            { key: 'open', label: 'Open' },
            { key: 'confirmed', label: 'Confirmed' },
            { key: 'rejected', label: 'Rejected' },
          ]}
          selected={statusFilter}
          onChange={setStatusFilter}
        />
      </div>

      {filtered.length === 0 ? (
        <EmptyState icon="🔔" message="No alerts match your filters" />
      ) : (
        <DataTable
          columns={columns}
          rows={filtered.map(a => ({ ...a } as unknown as Record<string, unknown>))}
          onRowClick={row => navigate(`/alerts/${row.event_id}`)}
          rowKey={r => String(r.event_id)}
        />
      )}
    </div>
  )
}
```

- [ ] **Step 2: Write AlertDetail**

Create `frontend/src/pages/AlertDetail.tsx`:
```typescript
import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import TimeSeriesChart from '../components/TimeSeriesChart'
import EmptyState from '../components/EmptyState'
import { submitFeedback, type AlertEvent } from '../api'

interface AlertDetailProps {
  alerts: AlertEvent[]
}

export default function AlertDetail({ alerts }: AlertDetailProps) {
  const { eventId } = useParams<{ eventId: string }>()
  const navigate = useNavigate()
  const [note, setNote] = useState('')
  const [feedbackStatus, setFeedbackStatus] = useState<string>()

  const alert = alerts.find(a => a.event_id === eventId)

  if (!alert) {
    return <EmptyState icon="🔍" message="Alert not found" />
  }

  const evidence = alert.evidence as Record<string, number | boolean>
  const evidenceKeys = Object.keys(evidence).filter(k => k !== 'roc_violation')

  const handleFeedback = async (confirmed: boolean) => {
    try {
      await submitFeedback(alert.event_id, confirmed)
      setFeedbackStatus(confirmed ? 'confirmed' : 'rejected')
    } catch {
      // Show error toast in production
    }
  }

  // Mock chart data around alert time
  const alertTime = new Date(alert.timestamp)
  const chartData: [string, number][] = Array.from({ length: 40 }, (_, i) => [
    new Date(alertTime.getTime() + (i - 20) * 60000).toISOString(),
    28 + Math.sin(i * 0.3) * 3 + (i === 20 ? 55 : 0),
  ])

  return (
    <div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <button onClick={() => navigate('/alerts')} style={{ background: 'none', border: 'none', color: '#64748b', fontSize: 11, cursor: 'pointer' }}>
          ← Back to Alerts
        </button>
        <span style={{ color: '#334155' }}>|</span>
        <span style={{ color: '#e2e8f0', fontWeight: 600, fontSize: 12 }}>Alert Detail</span>
        <span style={{ color: '#64748b', fontSize: 10, fontFamily: 'monospace' }}>{alert.event_id.slice(0, 8)}...</span>
      </div>

      <div style={{ display: 'flex', gap: 10 }}>
        <div style={{ flex: 2 }}>
          <div className="section-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 8 }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: 16, fontWeight: 700, color: alert.severity === 'critical' ? '#ef4444' : alert.severity === 'warning' ? '#f97316' : '#3b82f6' }}>
                    {alert.severity.charAt(0).toUpperCase() + alert.severity.slice(1)}
                  </span>
                  <span style={{ background: '#7f1d1d', color: '#fca5a5', padding: '2px 8px', borderRadius: 4, fontSize: 9 }}>
                    Score: {alert.anomaly_score.toFixed(2)}
                  </span>
                </div>
                <div style={{ color: '#94a3b8', fontSize: 11, marginTop: 4 }}>
                  {alert.device_id} / {alert.sensor_id} · {new Date(alert.timestamp).toLocaleString()}
                </div>
              </div>
              <span style={{ fontSize: 10, color: '#64748b' }}>Detection: {alert.detection_source}</span>
            </div>

            <div className="evidence-panel">
              <div className="evidence-panel-title">Evidence</div>
              <div className="evidence-grid">
                {evidenceKeys.map(k => (
                  <div key={k}>
                    <div className="evidence-item-label">{k}</div>
                    <div className="evidence-item-value">
                      {typeof evidence[k] === 'number' ? Number(evidence[k]).toFixed(4) : String(evidence[k])}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <TimeSeriesChart
            series={[{ name: alert.sensor_id, color: '#38bdf8', data: chartData }]}
            height={200}
            title="Context Window — ±30 min around event"
            anomalyPoints={[{ time: alert.timestamp, value: alert.evidence && typeof alert.evidence === 'object' && 'value' in alert.evidence ? Number(alert.evidence.value) : 85 }]}
          />
        </div>

        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 8 }}>
          <div className="section-card">
            <div className="section-card-title">Feedback</div>
            <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
              <button className="feedback-confirm" onClick={() => handleFeedback(true)}>✓ Confirm</button>
              <button className="feedback-reject" onClick={() => handleFeedback(false)}>✗ Reject</button>
            </div>
            <div style={{ marginTop: 8 }}>
              <input className="form-input" placeholder="Add note (optional)" value={note} onChange={e => setNote(e.target.value)} />
            </div>
            {feedbackStatus && (
              <div style={{ marginTop: 8, fontSize: 10, color: feedbackStatus === 'confirmed' ? '#86efac' : '#fca5a5' }}>
                {feedbackStatus === 'confirmed' ? '✓ Confirmed' : '✗ Rejected'}
              </div>
            )}
          </div>

          <div className="section-card">
            <div className="section-card-title">Alert Info</div>
            <div style={{ fontSize: 10 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                <span style={{ color: '#64748b' }}>Event ID</span>
                <span style={{ color: '#94a3b8', fontFamily: 'monospace' }}>{alert.event_id.slice(0, 13)}...</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 3 }}>
                <span style={{ color: '#64748b' }}>Source</span>
                <span style={{ color: '#94a3b8' }}>{alert.detection_source}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: '#64748b' }}>Status</span>
                <span style={{ color: alert.status === 'open' ? '#fca5a5' : '#86efac' }}>{alert.status}</span>
              </div>
            </div>
          </div>

          <div className="section-card">
            <div className="section-card-title">Related Alerts</div>
            {alerts.filter(a => a.device_id === alert.device_id && a.sensor_id === alert.sensor_id && a.event_id !== alert.event_id).slice(0, 3).map(a => (
              <div key={a.event_id} style={{ fontSize: 9, color: '#94a3b8', marginTop: 3 }}>
                {a.severity.toUpperCase()} {a.anomaly_score.toFixed(2)} · {new Date(a.timestamp).toLocaleTimeString()}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Write AlertsPage test**

Create `frontend/src/pages/__tests__/AlertsPage.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import AlertsPage from '../AlertsPage'

const mockAlerts = [{
  event_id: '1', device_id: 'pump-001', sensor_id: 'temp-01', sensor_type: 'temperature',
  anomaly_score: 0.95, severity: 'critical' as const, detection_source: 'statistical',
  timestamp: '2026-05-25T10:00:00Z', evidence: {}, status: 'open',
}]

describe('AlertsPage', () => {
  it('renders filter tabs', () => {
    render(
      <MemoryRouter>
        <AlertsPage alerts={mockAlerts} />
      </MemoryRouter>
    )
    expect(screen.getByText('Critical')).toBeInTheDocument()
    expect(screen.getByText('Open')).toBeInTheDocument()
  })

  it('shows alert in table', () => {
    render(
      <MemoryRouter>
        <AlertsPage alerts={mockAlerts} />
      </MemoryRouter>
    )
    expect(screen.getByText('pump-001')).toBeInTheDocument()
  })

  it('shows empty state when no alerts', () => {
    render(
      <MemoryRouter>
        <AlertsPage alerts={[]} />
      </MemoryRouter>
    )
    expect(screen.getByText('No alerts match your filters')).toBeInTheDocument()
  })
})
```

- [ ] **Step 4: Write AlertDetail test**

Create `frontend/src/pages/__tests__/AlertDetail.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { Route, Routes } from 'react-router-dom'
import AlertDetail from '../AlertDetail'

const mockAlerts = [{
  event_id: 'c88d1cbb-2737', device_id: 'pump-001', sensor_id: 'temp-01',
  sensor_type: 'temperature', anomaly_score: 0.95, severity: 'critical' as const,
  detection_source: 'statistical', timestamp: '2026-05-25T10:00:00Z',
  evidence: { value: 85.0, mean: 29.9, std: 2.3, z_score: 10.83, sigma: 3.0, window_size: 60 },
  status: 'open',
}]

describe('AlertDetail', () => {
  it('renders alert severity', async () => {
    render(
      <MemoryRouter initialEntries={['/alerts/c88d1cbb-2737']}>
        <Routes>
          <Route path="/alerts/:eventId" element={<AlertDetail alerts={mockAlerts} />} />
        </Routes>
      </MemoryRouter>
    )
    expect(await screen.findByText('Critical')).toBeInTheDocument()
  })

  it('shows confirm and reject buttons', async () => {
    render(
      <MemoryRouter initialEntries={['/alerts/c88d1cbb-2737']}>
        <Routes>
          <Route path="/alerts/:eventId" element={<AlertDetail alerts={mockAlerts} />} />
        </Routes>
      </MemoryRouter>
    )
    expect(await screen.findByText('✓ Confirm')).toBeInTheDocument()
    expect(screen.getByText('✗ Reject')).toBeInTheDocument()
  })

  it('shows empty state for unknown event id', () => {
    render(
      <MemoryRouter initialEntries={['/alerts/unknown-id']}>
        <Routes>
          <Route path="/alerts/:eventId" element={<AlertDetail alerts={[]} />} />
        </Routes>
      </MemoryRouter>
    )
    expect(screen.getByText('Alert not found')).toBeInTheDocument()
  })
})
```

- [ ] **Step 5: Run tests**

```bash
cd frontend && npx vitest run src/pages/__tests__/AlertsPage.test.tsx src/pages/__tests__/AlertDetail.test.tsx
```
Expected: 6 tests pass

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/AlertsPage.tsx frontend/src/pages/AlertDetail.tsx frontend/src/pages/__tests__/AlertsPage.test.tsx frontend/src/pages/__tests__/AlertDetail.test.tsx
git commit -m "feat: add AlertsPage with filters and AlertDetail with feedback actions"
```

---

### Task 11: TrainingPage + SettingsPage

**Files:**
- Create: `frontend/src/pages/TrainingPage.tsx`
- Create: `frontend/src/pages/SettingsPage.tsx`
- Test: `frontend/src/pages/__tests__/TrainingPage.test.tsx`
- Test: `frontend/src/pages/__tests__/SettingsPage.test.tsx`

- [ ] **Step 1: Write TrainingPage**

Create `frontend/src/pages/TrainingPage.tsx`:
```typescript
import TimeSeriesChart from '../components/TimeSeriesChart'

interface ModelInfo {
  name: string
  status: 'active' | 'accumulating' | 'degraded'
  version: string
  dataPoints: number
  minRequired: number
  lastTrained: string
  latency: string
  reconError: number
}

const MOCK_MODELS: ModelInfo[] = [
  { name: 'Pump Model', status: 'active', version: 'v2.3.1', dataPoints: 850000, minRequired: 65000, lastTrained: 'May 20, 2026', latency: '0.4ms', reconError: 0.012 },
  { name: 'Fan Model', status: 'accumulating', version: '—', dataPoints: 12000, minRequired: 65000, lastTrained: 'Never', latency: '—', reconError: 0 },
]

// KL divergence mock data
const driftData: [string, number][] = [
  ['2026-05-01', 0.042], ['2026-05-03', 0.038], ['2026-05-06', 0.045],
  ['2026-05-09', 0.041], ['2026-05-12', 0.036], ['2026-05-15', 0.044],
  ['2026-05-18', 0.048], ['2026-05-21', 0.052], ['2026-05-24', 0.058], ['2026-05-25', 0.065],
]

export default function TrainingPage() {
  return (
    <div>
      <h2 style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 600, marginBottom: 12 }}>Model Status</h2>

      <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
        {MOCK_MODELS.map(m => (
          <div key={m.name} className="section-card" style={{ flex: 1 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <span style={{ color: '#e2e8f0', fontWeight: 600, fontSize: 11 }}>{m.name}</span>
              <span style={{
                padding: '2px 8px', borderRadius: 8, fontSize: 8,
                background: m.status === 'active' ? '#14532d' : '#7c2d12',
                color: m.status === 'active' ? '#86efac' : '#fdba74',
              }}>
                {m.status === 'active' ? 'Active' : 'Accumulating'}
              </span>
            </div>
            <div style={{ fontSize: 10, color: '#64748b', display: 'flex', flexDirection: 'column', gap: 3 }}>
              <div>Version: <span style={{ color: '#94a3b8' }}>{m.version}</span></div>
              <div>Training data: <span style={{ color: '#94a3b8' }}>{m.dataPoints.toLocaleString()} pts</span></div>
              <div>Last trained: <span style={{ color: '#94a3b8' }}>{m.lastTrained}</span></div>
              <div>Inference: <span style={{ color: '#94a3b8' }}>{m.latency}</span></div>
              {m.status === 'accumulating' && (
                <div style={{ marginTop: 4 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 8, marginBottom: 2 }}>
                    <span>Progress</span>
                    <span style={{ color: '#f97316' }}>{Math.round((m.dataPoints / m.minRequired) * 100)}%</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-bar-fill" style={{ width: `${(m.dataPoints / m.minRequired) * 100}%`, background: '#f97316' }} />
                  </div>
                </div>
              )}
              {m.status === 'active' && (
                <div style={{ marginTop: 4 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 8, marginBottom: 2 }}>
                    <span>Recon Error</span><span style={{ color: '#22c55e' }}>{m.reconError}</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-bar-fill" style={{ width: `${m.reconError * 1000}%`, background: '#22c55e' }} />
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="section-card">
        <div className="chart-header">
          <span className="chart-title">Concept Drift — KL Divergence (Pump Model)</span>
          <span style={{ fontSize: 9, color: '#64748b' }}>30-day window</span>
        </div>
        <TimeSeriesChart
          series={[{ name: 'KL Divergence', color: '#8b5cf6', data: driftData }]}
          height={200}
        />
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Write SettingsPage**

Create `frontend/src/pages/SettingsPage.tsx`:
```typescript
export default function SettingsPage() {
  return (
    <div>
      <h2 style={{ color: '#e2e8f0', fontSize: 14, fontWeight: 600, marginBottom: 12 }}>Settings</h2>

      <div className="section-card">
        <div className="section-card-title">Notification Channels</div>
        {[
          { name: 'DingTalk', url: 'https://oapi.dingtalk.com/robot/...', type: 'Webhook', enabled: true },
          { name: 'Email', url: 'ops-team@example.com', type: 'SMTP', enabled: true },
          { name: 'Feishu', url: 'Not configured', type: 'Webhook', enabled: false },
        ].map(ch => (
          <div key={ch.name} style={{
            display: 'flex', alignItems: 'center', gap: 8, padding: '6px 8px',
            background: '#0f172a', borderRadius: 3, marginBottom: 6,
          }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', background: ch.enabled ? '#22c55e' : '#334155' }} />
            <span style={{ color: ch.enabled ? '#e2e8f0' : '#64748b', fontSize: 10, flex: 1 }}>{ch.name}</span>
            <span style={{ color: '#64748b', fontSize: 9, background: '#1e293b', padding: '2px 8px', borderRadius: 3 }}>{ch.url}</span>
            <span style={{ color: '#64748b', fontSize: 9 }}>{ch.type}</span>
            <button className="btn-primary" style={{ fontSize: 9, padding: '2px 8px' }}>
              {ch.enabled ? 'Edit' : '+ Add'}
            </button>
          </div>
        ))}
      </div>

      <div className="section-card">
        <div className="section-card-title">Global Parameters</div>
        <div className="config-row">
          {[
            { label: 'Alert Cooldown (min)', value: '5' },
            { label: 'Data Retention (days)', value: '90' },
            { label: 'Retrain Interval (days)', value: '30' },
          ].map(field => (
            <div className="config-field" key={field.label}>
              <div className="form-label">{field.label}</div>
              <input className="form-input" defaultValue={field.value} />
            </div>
          ))}
          <button className="btn-primary" style={{ alignSelf: 'flex-end' }}>Save</button>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 3: Write TrainingPage test**

Create `frontend/src/pages/__tests__/TrainingPage.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import TrainingPage from '../TrainingPage'

describe('TrainingPage', () => {
  it('renders model status heading', () => {
    render(<TrainingPage />)
    expect(screen.getByText('Model Status')).toBeInTheDocument()
  })

  it('renders Pump Model card', () => {
    render(<TrainingPage />)
    expect(screen.getByText('Pump Model')).toBeInTheDocument()
  })

  it('renders drift chart section', () => {
    render(<TrainingPage />)
    expect(screen.getByText('Concept Drift — KL Divergence (Pump Model)')).toBeInTheDocument()
  })
})
```

- [ ] **Step 4: Write SettingsPage test**

Create `frontend/src/pages/__tests__/SettingsPage.test.tsx`:
```typescript
import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import SettingsPage from '../SettingsPage'

describe('SettingsPage', () => {
  it('renders settings heading', () => {
    render(<SettingsPage />)
    expect(screen.getByText('Settings')).toBeInTheDocument()
  })

  it('renders notification channels', () => {
    render(<SettingsPage />)
    expect(screen.getByText('DingTalk')).toBeInTheDocument()
    expect(screen.getByText('Email')).toBeInTheDocument()
  })

  it('renders global parameters', () => {
    render(<SettingsPage />)
    expect(screen.getByText('Alert Cooldown (min)')).toBeInTheDocument()
  })
})
```

- [ ] **Step 5: Run tests**

```bash
cd frontend && npx vitest run src/pages/__tests__/TrainingPage.test.tsx src/pages/__tests__/SettingsPage.test.tsx
```
Expected: 6 tests pass

- [ ] **Step 6: Commit**

```bash
git add frontend/src/pages/TrainingPage.tsx frontend/src/pages/SettingsPage.tsx frontend/src/pages/__tests__/TrainingPage.test.tsx frontend/src/pages/__tests__/SettingsPage.test.tsx
git commit -m "feat: add TrainingPage with model cards and drift chart, and SettingsPage"
```

---

### Task 12: Integration — verify full app compiles and runs

**Files:**
- Modify: `frontend/src/api.ts` (add training types export)

- [ ] **Step 1: Remove old App.css reference from App.tsx**

Ensure `frontend/src/App.tsx` imports `./App.css` (already done in Task 7).

- [ ] **Step 2: Verify TypeScript compilation**

```bash
cd frontend && npx tsc -b --noEmit 2>&1 | head -30
```
Expected: no errors (or fix any type issues found)

- [ ] **Step 3: Run all tests**

```bash
cd frontend && npx vitest run 2>&1 | tail -20
```
Expected: all tests pass

- [ ] **Step 4: Start dev server and verify it boots**

```bash
cd frontend && npx vite --port 5175 &
sleep 3
curl -s http://localhost:5175/ | head -5
```
Expected: HTML page returns

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "chore: final integration — all pages, components, and tests verified"
```
