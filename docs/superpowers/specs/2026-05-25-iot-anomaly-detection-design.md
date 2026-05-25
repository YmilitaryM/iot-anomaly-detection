# IoT Sensor Anomaly Detection — Design Spec

## Overview

A general-purpose IoT sensor anomaly detection platform supporting multiple sensor types, both real-time streaming and offline batch analysis. Cloud-first deployment; architecture supports future edge expansion without redesign. Delivers API, web dashboard, and alerting channels.

## Requirements Summary

| Dimension | Decision |
|-----------|----------|
| Sensor types | General: vibration, temperature, humidity, pressure, current, power, discrete state |
| Data processing | Real-time streaming + offline batch analysis |
| Deployment | Cloud-first; architecture supports future edge expansion |
| Output | REST API + Web Dashboard + Alert notifications (DingTalk/Feishu/Email) |
| Scale target | 10k+ devices, 10k+ data points/sec; architecture scales from small |
| Labeled data | None at start; unsupervised/self-supervised approach required |

## Architecture Philosophy

**Progressive complexity, data-driven.** Start with the simplest system that delivers value, then add sophistication only when production data proves it's needed. Detection modules are plugin-based — easy to add or remove without architectural change.

## Detection Pipeline (Three-Phase Rollout)

### Phase 1: Baseline Pipeline (Week 1–2)

Purpose: fast time-to-value, data accumulation.

- MQTT data ingestion and protocol adaptation
- Hard boundary detection: per-sensor absolute min/max, enforces physical/safety limits. Short-circuits all other detection.
- Statistical rules: rate-of-change, deadband, sliding-window 3σ
- Alert deduplication: 5-minute cooldown per device+sensor pair
- Accumulate raw data into TimescaleDB for Phase 2 training

### Phase 2: LSTM-Autoencoder (Week 3–4)

Purpose: unified model replacing multiple statistical detectors.

Single Bidirectional LSTM Encoder + Unidirectional LSTM Decoder model:

- **Input**: sliding window [T-w, T] × all sensors of a device, as a multivariate time series fragment
- **Output**: reconstruction of the same window
- **Anomaly score**: per-sensor reconstruction error (MSE)
- **Training**: self-supervised — model learns to reconstruct "normal" windows

Key design decisions:

- **Self-cleaning training**: Round 1 train on all Phase 1 data → score and remove top 5% windows → Round 2 retrain on cleaned data
- **Preprocessing**: RobustScaler (median + IQR) per sensor, not min-max, to resist outlier influence
- **Per-sensor error**: each sensor's reconstruction error computed independently, thresholded independently via POT (Peak-Over-Threshold), not a single global MSE
- **Dynamic threshold**: POT fits a GPD (Generalized Pareto Distribution) to the upper tail of reconstruction errors. Threshold = (1-α) quantile, recalculated every 1000 windows. Automatically adapts to model aging.
- **Hard boundaries never retire**: Phase 1 hard limits remain as safety net

Model architecture:

| Hyperparameter | Value | Rationale |
|---------------|-------|-----------|
| Encoder | 2-layer BiLSTM, hidden=64–128 | Bidirectional captures context both ways |
| Decoder | 2-layer UniLSTM, hidden=64–128 | Unidirectional respects temporal causality |
| Window size | 64–256 steps | ≥ 5 sampling intervals, ≥ 2 seasonal cycles |
| Dropout | 0.2 | Prevents overfitting to exact normal patterns |
| Gradient clipping | 1.0 | Training stability |
| Inference | Export ONNX → ONNX Runtime | 0.3–1ms per window |

Minimum training data: ~65,000 raw data points per device type. At 1Hz this is ~18 hours; at 0.1Hz this is ~7.5 days. Phase 1 runs longer for low-frequency sensors.

**Model-per-device strategy**: one model per device type, not per individual device. Devices of the same type share a model, pooling training data. Per-device fine-tuning is a Phase 4 option if individual devices diverge.

Phase 2 deploys, it replaces Phase 1 statistical rules (3σ, rate-of-change) for sensors covered by the model. Hard boundaries are never disabled.

### Phase 3: Feedback Loop + Model Evolution (Week 5–6)

- Operator confirm/reject alerts → labeled data accumulation
- Feedback adjusts detection sensitivity per sensor
- Concept drift monitoring: KL divergence between recent error distribution and baseline → triggers retraining when drift detected
- Retraining: sliding window of last N days (default N=30), self-clean with current model, A/B validate before switch
- Minimum retraining interval: 7 days

### Phase 4+: Needs-Driven Extensions

Each extension is triggered by specific production findings, not pre-designed:

- Operating mode awareness: added only if mode changes cause significant false positives for a specific equipment type
- Change point detection (PELT): added if regime-shift anomalies are missed
- VAE upgrade: replace AE if reconstruction probability proves more reliable than raw error
- Transformer: replace LSTM if data volume justifies it and long-range dependency matters

## Data Model

### Sensor Data Point (incoming)
```
device_id: str
sensor_id: str
sensor_type: enum[temperature, vibration, pressure, current, power, humidity, discrete]
value: float
timestamp: datetime
unit: str (optional)
```

### Anomaly Event (outgoing)
```
event_id: uuid
device_id: str
sensor_id: str
sensor_type: enum
timestamp: datetime
anomaly_score: float (0–1)
severity: enum[critical, warning, info]
detection_source: enum[hard_boundary, lstm_ae, statistical, ...]
evidence: json (per-sensor reconstruction error, threshold at time, window context)
status: enum[open, confirmed, rejected]
confirmed_by: str (operator id, nullable)
confirmed_at: datetime (nullable)
```

### Device Metadata
```
device_id: str
device_type: str
sensors: list[sensor_config]
training_status: enum[accumulating, training, active, degraded]
model_version: str
```

## System Architecture

```
┌─────────────┐    ┌──────────────┐    ┌──────────────────┐
│ MQTT Broker  │───→│ Bytewax      │───→│ Detection Engine │
│   (EMQX)     │    │ (stream proc)│    │  ┌────────────┐  │
└─────────────┘    └──────────────┘    │  │Hard Bounds │  │
                                       │  ├────────────┤  │
                                       │  │ LSTM-AE    │  │
                                       │  │ (ONNX RT)  │  │
                                       │  ├────────────┤  │
                                       │  │Plugin Slots│  │
                                       │  └────────────┘  │
                                       └────────┬─────────┘
                                                │
                    ┌───────────────────────────┼──────────────┐
                    │                           │              │
              ┌─────▼─────┐            ┌───────▼──────┐  ┌────▼─────┐
              │ TimescaleDB│            │  PostgreSQL   │  │  Redis   │
              │(raw+agg)  │            │(meta+alerts) │  │(cache)  │
              └───────────┘            └──────────────┘  └──────────┘
                    │                           │
              ┌─────▼─────┐            ┌───────▼──────┐
              │PyTorch    │            │   FastAPI     │
              │(training) │            │  (API+alerts) │
              └───────────┘            └───────┬───────┘
                                               │
                                        ┌──────▼──────┐
                                        │ React+ECharts│
                                        │ (dashboard)  │
                                        └─────────────┘
```

## Technology Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Message broker | EMQX | Open-source, million-connection scale |
| Stream processing | Bytewax | Python-native, lighter than Flink; sufficient for feature extraction + inference dispatch |
| Model training | PyTorch + Lightning | Standard DL stack |
| Model inference | ONNX Runtime | 3-10x faster than raw PyTorch; edge-compatible |
| Time-series DB | TimescaleDB | PostgreSQL extension, SQL-native, good for structured sensor data |
| Relational DB | PostgreSQL | Device metadata, alert events, user feedback |
| Cache | Redis | Sliding window buffer, alert dedup, real-time device state |
| Web backend | FastAPI | Async Python, websocket support for real-time dashboard push |
| Frontend | React + ECharts | Component library + high-performance time-series charts |
| Containerization | Docker Compose (dev) / K8s (prod) | Gradual complexity |

## Error Handling & Edge Cases

- **Sensor disconnection**: stale data detection — if no data received for > 3× expected sampling interval, emit device_offline event
- **Burst data on reconnect**: dedup by (device_id, sensor_id, timestamp); late-arriving data processed in batch path
- **Model cold start**: Phase 1 hard boundaries + statistical rules always active; model only takes over when training_status = "active"
- **Concept drift**: KL divergence monitoring triggers retraining; if retraining fails validation, fall back to Phase 1 rules
- **Alert storm**: 5-minute cooldown per device+sensor; global rate limiter on notification channels
- **Model inference failure**: timeout (100ms) → skip LSTM-AE, fall back to statistical rules for that window

## Testing Strategy

- **Unit tests**: each detector in isolation with synthetic data (known anomalies injected)
- **Integration tests**: end-to-end pipeline from MQTT message to alert event
- **Model validation**: hold-out normal data → reconstruction error should be low; injected anomalies → should spike
- **Backtesting**: replay historical data with known incidents, measure detection rate and latency
- **A/B testing**: Phase 3 model retraining — compare new vs old model on live traffic before switch
