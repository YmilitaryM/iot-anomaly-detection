# IoT Anomaly Detection Dashboard — Design Spec

## Overview

全功能管理后台仪表板，覆盖设备监控、告警管理、模型训练和系统配置。Industrial Dark 设计语言，顶部导航+侧边栏架构，React + TypeScript + ECharts 技术栈。

## Design Decisions

| Dimension | Decision |
|-----------|----------|
| Visual style | Industrial Dark: #0f172a bg, #1e293b panels, #38bdf8 accent |
| Navigation | Top nav bar (5 sections) + left sidebar (sub-nav) |
| Charts | ECharts via echarts-for-react |
| Real-time | WebSocket for live alerts, polling for device list refresh |
| Responsive | Desktop-first (1920px target), panels collapse on <1280px |

## Page Architecture

### 1. Overview (Dashboard)

Purpose: 运维人员打开即见全局状态。

- **Stat cards row**: Critical/Warning/Healthy counts + Throughput, each with trend sparkline and delta indicator
- **Time range selector**: 1h / 6h / 24h / 7d pill buttons
- **Main chart**: Large time-series, multi-sensor overlay with legend toggles, anomaly bands highlighted in red
- **Bottom left: Alert feed**: Last 5 alerts with severity color coding, click to navigate
- **Bottom right: Device health donut**: Healthy/Warning/Critical distribution

### 2. Devices

Purpose: 设备管理和传感器配置。

**List view:**
- Search bar + Type/Status filter dropdowns
- Table: Device ID, Type, Sensor Count, Status badge, Training Status, drill-down arrow
- Status badges: Critical (red), Warning (orange), Healthy (green)

**Detail view (click-through):**
- Breadcrumb back-link + device header with status badge
- Sensor cards row: one card per sensor — current value, mini sparkline, sensor type label, color-coded accent border
- Multi-sensor overlaid time-series chart with legend
- Hard Boundary Config panel: Min/Max/Deadband inputs + Save button
- Recent Alerts for this device: last 5, clickable

### 3. Alerts

Purpose: 告警全生命周期管理——发现、调查、反馈。

**Feed view:**
- Severity filter tabs: All / Critical / Warning / Info
- Status filter tabs: Open / Confirmed / Rejected
- Sort selector: Newest / Oldest / Highest score
- Table: Severity dot, Device, Sensor, Detection Source, Anomaly Score, Timestamp, Status badge, drill-down

**Detail view (click-through):**
- Header: Severity label + Anomaly Score + device/sensor + timestamp
- Evidence panel: Value, Mean, Std Dev, Z-Score, Sigma, Window Size — all extracted from detection evidence JSON
- Context chart: time-series with anomaly point marked and vertical guideline, ±30 min window
- Feedback actions: Confirm (green) / Reject (red) buttons + optional note input
- Sidebar: Event ID, Detection Source, Dedup Count, Status
- Related Alerts: same device+sensor, last 7 days

### 4. Training

Purpose: 模型生命周期管理。

- **Model cards**: one per device type — model name, version, training data volume, last trained date, inference latency, reconstruction error gauge
- **Status badges**: Active (green), Accumulating (orange with progress bar toward 65k minimum), Degraded (red), Training (blue)
- **Drift monitor chart**: KL divergence over 30-day window, retrain threshold line, X-axis date labels

### 5. Settings

Purpose: 系统级配置。

- **Notification channels**: DingTalk (webhook URL), Email (SMTP + address), Feishu (webhook URL) — each with enable/disable toggle and edit
- **Global parameters**: Alert Cooldown (minutes), Data Retention (days), Retrain Interval (days) — number inputs with save

## Component Tree

```
App
├── TopNav (section switcher: Overview/Devices/Alerts/Training/Settings)
├── Sidebar (sub-nav, context-dependent)
└── MainContent (react-router)
    ├── OverviewPage
    │   ├── StatCard (×4, with sparkline)
    │   ├── TimeRangeSelector
    │   ├── TimeSeriesChart (large, multi-sensor)
    │   ├── AlertFeed (compact list)
    │   └── HealthDonut
    ├── DevicesPage
    │   ├── DeviceList
    │   │   ├── SearchBar
    │   │   ├── FilterDropdowns
    │   │   └── DeviceTable
    │   └── DeviceDetail
    │       ├── SensorCard (×N, with mini sparkline)
    │       ├── TimeSeriesChart (multi-sensor)
    │       ├── HardBoundaryConfig
    │       └── DeviceAlertList
    ├── AlertsPage
    │   ├── AlertFeed
    │   │   ├── FilterTabs (severity + status)
    │   │   └── AlertTable
    │   └── AlertDetail
    │       ├── EvidencePanel
    │       ├── ContextChart (with anomaly marker)
    │       ├── FeedbackActions
    │       └── RelatedAlerts
    ├── TrainingPage
    │   ├── ModelCard (×N)
    │   └── DriftChart (KL divergence)
    └── SettingsPage
        ├── NotificationChannelList
        └── GlobalConfigForm
```

## Reusable Components

| Component | Props | Used In |
|-----------|-------|---------|
| StatCard | label, value, delta, trendData, accentColor | Overview |
| TimeSeriesChart | data, seriesConfig, height, showAnomalies | Overview, DeviceDetail, AlertDetail |
| StatusBadge | severity/status, size | Everywhere |
| SeverityDot | severity | AlertTable, AlertFeed |
| FilterTabs | options, selected, onChange | Alerts, Devices |
| DataTable | columns, rows, onRowClick | Devices, Alerts |
| MiniSparkline | data, color, width, height | SensorCard |

## Data Flow

```
WebSocket /ws/alerts ──→ AlertEvent[] ──→ AlertFeed (real-time prepend)
                                              └── AlertDetail
                                              └── StatCard counts

GET /api/devices ──→ Device[] ──→ DeviceTable
                      └── registerDevice() on ingest

GET /api/data/sensors/{device}/{sensor}?start&end ──→ SensorData[] ──→ TimeSeriesChart

GET /api/alerts?limit&offset ──→ AlertEvent[] ──→ AlertTable

POST /api/alerts/{id}/feedback?confirmed= ──→ update alert status
```

- Device list polls every 5 seconds
- Chart data polls every 5 seconds when sensor is selected
- Alerts arrive via WebSocket in real-time; initial load via REST
- Feedback POST updates alert status optimistically then confirms

## API Requirements (new endpoints needed)

Existing endpoints are sufficient for core functionality. One addition needed:

```
GET /api/training/status — returns model cards data per device type
  [{device_type, model_version, training_status, data_points, min_required,
    last_trained, inference_latency_ms, recon_error, drift_kl}]
```

## Error & Edge Cases

- **Empty state**: each list/table shows "No data yet" placeholder with contextual help text
- **WebSocket disconnected**: TopNav dot turns red, shows "Disconnected", auto-reconnect every 3s
- **Chart loading**: skeleton placeholder while data fetches
- **Feedback failure**: toast notification on failed confirm/reject, retry button
- **Long device/sensor names**: truncate with tooltip on hover

## Testing Strategy

- Component unit tests: each reusable component renders with mock props
- Page integration tests: mock API responses, verify correct rendering
- WebSocket tests: mock WebSocket server, verify alert prepend
- E2E: ingest data → verify devices appear → select device → chart renders → inject anomaly → alert appears

## File Structure

```
frontend/src/
├── main.tsx
├── App.tsx                    # Router + layout shell
├── App.css                    # Global styles + CSS variables
├── api.ts                     # API client (extend with training endpoint)
├── useWebSocket.ts            # WebSocket hook (existing, reuse)
├── components/                # Reusable components
│   ├── StatCard.tsx
│   ├── TimeSeriesChart.tsx
│   ├── StatusBadge.tsx
│   ├── SeverityDot.tsx
│   ├── FilterTabs.tsx
│   ├── DataTable.tsx
│   ├── MiniSparkline.tsx
│   └── EmptyState.tsx
├── pages/                     # Page components
│   ├── OverviewPage.tsx
│   ├── DevicesPage.tsx
│   ├── DeviceDetail.tsx
│   ├── AlertsPage.tsx
│   ├── AlertDetail.tsx
│   ├── TrainingPage.tsx
│   └── SettingsPage.tsx
└── hooks/                     # Custom hooks
    ├── usePolling.ts          # Generic polling hook
    └── useChartData.ts        # Chart data fetching hook
```
