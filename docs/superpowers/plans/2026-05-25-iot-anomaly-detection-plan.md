# IoT Sensor Anomaly Detection — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a general-purpose IoT sensor anomaly detection platform that ingests MQTT data, detects anomalies via statistical rules and LSTM-Autoencoder, and delivers results through API, dashboard, and alert channels.

**Architecture:** Plugin-based detection engine with progressive complexity. Phase 1 delivers baseline statistical detection with hard boundaries. Phase 2 adds LSTM-Autoencoder as unified model. Phase 3 closes the feedback loop with drift monitoring. Detectors implement a common interface and are hot-swappable via configuration.

**Tech Stack:** Python 3.11, FastAPI, PyTorch, ONNX Runtime, EMQX, PostgreSQL+TimescaleDB, Redis, Docker Compose

---

## File Structure Map

```
src/
├── config.py                  # Pydantic Settings for all configuration
├── models/
│   ├── sensor.py              # SensorData, SensorType, SensorConfig
│   ├── anomaly.py             # AnomalyEvent, Severity, DetectionSource
│   └── device.py              # DeviceMetadata, TrainingStatus
├── ingestion/
│   └── mqtt.py                # Async MQTT client (aiomqtt)
├── detection/
│   ├── base.py                # Abstract Detector ABC
│   ├── hard_boundary.py       # Hard physical/safety limits
│   ├── statistical.py         # Rate-of-change, 3-sigma, deadband
│   ├── lstm_ae.py             # LSTM-AE detector (ONNX inference)
│   └── engine.py              # Orchestrator, merges detector outputs
├── threshold/
│   └── pot.py                 # Peak-Over-Threshold dynamic threshold
├── preprocessing/
│   └── scaler.py              # RobustScaler per sensor
├── alerting/
│   ├── dedup.py               # 5-min cooldown dedup
│   ├── channels.py            # DingTalk, Feishu, Email, Console
│   └── router.py              # Severity-based routing
├── storage/
│   ├── timescaledb.py         # Raw data + aggregate storage
│   ├── postgres.py            # Device meta, alert events, feedback
│   └── redis.py               # Window buffer, dedup state, rate limits
├── training/
│   ├── model.py               # BiLSTM-encoder + UniLSTM-decoder
│   ├── dataset.py             # SlidingWindowDataset
│   ├── train.py               # Training loop with early stopping
│   ├── self_cleaning.py       # Two-round self-cleaning
│   └── export_onnx.py         # PyTorch → ONNX export
├── drift/
│   └── monitor.py             # KL divergence drift detection
├── feedback/
│   └── collector.py           # Operator confirm/reject processing
├── api/
│   ├── app.py                 # FastAPI app factory
│   ├── deps.py                # Dependency injection
│   ├── routes/
│   │   ├── alerts.py          # Alert CRUD + feedback
│   │   ├── devices.py         # Device registration + config
│   │   └── data.py            # Sensor data query
│   └── websocket.py           # Real-time alert push
├── cli/
│   └── simulate.py            # Sensor simulator for testing/dev
└── main.py                    # Entrypoint: start ingestion + API

tests/
├── conftest.py                # Shared fixtures
├── test_hard_boundary.py
├── test_statistical.py
├── test_pot.py
├── test_scaler.py
├── test_dedup.py
├── test_detection_engine.py
├── test_alert_router.py
├── test_lstm_ae_model.py
├── test_training.py
├── test_api.py
└── test_integration.py

docker-compose.yml
Dockerfile
```

---

### Task 1: Project Setup and Dependencies

**Files:**
- Modify: `pyproject.toml`
- Create: `src/__init__.py`, `src/config.py`

- [ ] **Step 1: Update pyproject.toml with all dependencies**

```toml
[project]
name = "iot-anomaly-detection"
version = "0.1.0"
description = "IoT sensor anomaly detection platform"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    "aiomqtt>=2.0",
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "websockets>=12",
    "pydantic>=2.0",
    "pydantic-settings>=2.0",
    "sqlalchemy[asyncio]>=2.0",
    "asyncpg>=0.29",
    "redis[hiredis]>=5.0",
    "httpx>=0.27",
    "numpy>=1.26",
    "scipy>=1.12",
    "torch>=2.2",
    "onnx>=1.16",
    "onnxruntime>=1.18",
    "scikit-learn>=1.4",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.23",
    "pytest-cov>=5.0",
    "httpx>=0.27",
    "aiomqtt>=2.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

- [ ] **Step 2: Create src/__init__.py**

```python
"""IoT Anomaly Detection Platform."""
```

- [ ] **Step 3: Create src/config.py**

```python
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "IOT_", "env_nested_delimiter": "__"}

    # MQTT
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic: str = "sensors/#"

    # PostgreSQL
    postgres_dsn: str = "postgresql+asyncpg://iot:iot@localhost:5432/iot"

    # TimescaleDB (same PG instance, different schema handling)
    timescale_dsn: str = "postgresql+asyncpg://iot:iot@localhost:5432/iot"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Detection
    dedup_window_seconds: int = 300
    hard_boundary_enabled: bool = True
    statistical_enabled: bool = True
    lstm_ae_enabled: bool = False
    statistical_window_size: int = 100
    statistical_sigma: float = 3.0

    # Model
    model_dir: Path = Path("models")
    model_window_size: int = 128
    model_hidden_dim: int = 64
    training_min_samples: int = 65_000

    # POT
    pot_alpha: float = 0.001
    pot_window: int = 1000

    # Alerting
    dingtalk_webhook: str = ""
    feishu_webhook: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_from_email: str = ""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000


settings = Settings()
```

- [ ] **Step 4: Install dependencies and verify**

```bash
cd /Users/ymilitarym/hp-2026/iot-anomaly-detection
pip install -e ".[dev]"
python -c "from src.config import settings; print(settings.mqtt_host)"
```

Expected: prints "localhost"

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/__init__.py src/config.py
git commit -m "feat: project setup with dependencies and configuration"
```

---

### Task 2: Data Models

**Files:**
- Create: `src/models/__init__.py`
- Create: `src/models/sensor.py`
- Create: `src/models/anomaly.py`
- Create: `src/models/device.py`

- [ ] **Step 1: Create src/models/__init__.py**

```python
from src.models.sensor import SensorData, SensorType, SensorConfig
from src.models.anomaly import AnomalyEvent, Severity, DetectionSource, AnomalyStatus
from src.models.device import DeviceMetadata, TrainingStatus

__all__ = [
    "SensorData", "SensorType", "SensorConfig",
    "AnomalyEvent", "Severity", "DetectionSource", "AnomalyStatus",
    "DeviceMetadata", "TrainingStatus",
]
```

- [ ] **Step 2: Create src/models/sensor.py**

```python
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field


class SensorType(StrEnum):
    TEMPERATURE = "temperature"
    VIBRATION = "vibration"
    PRESSURE = "pressure"
    CURRENT = "current"
    POWER = "power"
    HUMIDITY = "humidity"
    DISCRETE = "discrete"


class SensorData(BaseModel):
    device_id: str
    sensor_id: str
    sensor_type: SensorType
    value: float
    timestamp: datetime
    unit: str | None = None


class SensorConfig(BaseModel):
    sensor_id: str
    sensor_type: SensorType
    unit: str | None = None
    hard_min: float | None = None
    hard_max: float | None = None
    expected_interval_seconds: float = 1.0
```

- [ ] **Step 3: Create src/models/anomaly.py**

```python
import uuid
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field


class Severity(StrEnum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class DetectionSource(StrEnum):
    HARD_BOUNDARY = "hard_boundary"
    STATISTICAL = "statistical"
    LSTM_AE = "lstm_ae"


class AnomalyStatus(StrEnum):
    OPEN = "open"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class AnomalyEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    sensor_id: str
    sensor_type: str
    timestamp: datetime
    anomaly_score: float
    severity: Severity
    detection_source: DetectionSource
    evidence: dict = Field(default_factory=dict)
    status: AnomalyStatus = AnomalyStatus.OPEN
    confirmed_by: str | None = None
    confirmed_at: datetime | None = None
```

- [ ] **Step 4: Create src/models/device.py**

```python
from enum import StrEnum
from pydantic import BaseModel, Field


class TrainingStatus(StrEnum):
    ACCUMULATING = "accumulating"
    TRAINING = "training"
    ACTIVE = "active"
    DEGRADED = "degraded"


class DeviceMetadata(BaseModel):
    device_id: str
    device_type: str
    display_name: str = ""
    sensor_configs: list = Field(default_factory=list)
    training_status: TrainingStatus = TrainingStatus.ACCUMULATING
    model_version: str = ""
```

- [ ] **Step 5: Run quick import test**

```bash
python -c "from src.models import SensorData, AnomalyEvent, DeviceMetadata; print('ok')"
```

Expected: prints "ok"

- [ ] **Step 6: Commit**

```bash
git add src/models/
git commit -m "feat: add data models for sensor, anomaly, and device"
```

---

### Task 3: Detector Base Interface

**Files:**
- Create: `src/detection/__init__.py`
- Create: `src/detection/base.py`
- Test: `tests/__init__.py`, `tests/conftest.py`

- [ ] **Step 1: Create src/detection/__init__.py**

```python
"""Pluggable detection engine."""
```

- [ ] **Step 2: Create src/detection/base.py**

```python
from abc import ABC, abstractmethod
from collections.abc import Sequence
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent


class Detector(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def detect(self, data: SensorData, history: Sequence[SensorData]) -> AnomalyEvent | None:
        """Return AnomalyEvent if anomaly detected, None otherwise."""
        ...

    @abstractmethod
    def configure(self, **kwargs) -> None:
        """Update detector parameters at runtime."""
        ...
```

- [ ] **Step 3: Create tests/__init__.py (empty file)**

```bash
touch tests/__init__.py
```

- [ ] **Step 4: Create tests/conftest.py**

```python
import pytest
from datetime import datetime, timedelta
from src.models.sensor import SensorData, SensorType


def make_sensor_data(
    device_id: str = "dev-001",
    sensor_id: str = "temp-01",
    sensor_type: SensorType = SensorType.TEMPERATURE,
    value: float = 25.0,
    timestamp: datetime | None = None,
) -> SensorData:
    return SensorData(
        device_id=device_id,
        sensor_id=sensor_id,
        sensor_type=sensor_type,
        value=value,
        timestamp=timestamp or datetime.now(),
    )


def make_history(
    base_value: float,
    count: int,
    noise: float = 0.0,
    interval_seconds: float = 1.0,
    start_time: datetime | None = None,
    device_id: str = "dev-001",
    sensor_id: str = "temp-01",
) -> list[SensorData]:
    import random
    random.seed(42)
    t = start_time or datetime.now() - timedelta(seconds=count * interval_seconds)
    history = []
    for i in range(count):
        val = base_value + random.gauss(0, noise) if noise > 0 else base_value
        history.append(SensorData(
            device_id=device_id,
            sensor_id=sensor_id,
            sensor_type=SensorType.TEMPERATURE,
            value=val,
            timestamp=t + timedelta(seconds=i * interval_seconds),
        ))
    return history
```

- [ ] **Step 5: Commit**

```bash
git add src/detection/ tests/
git commit -m "feat: add detector base interface and test fixtures"
```

---

### Task 4: Hard Boundary Detector

**Files:**
- Create: `src/detection/hard_boundary.py`
- Test: `tests/test_hard_boundary.py`

- [ ] **Step 1: Write the failing test — tests/test_hard_boundary.py**

```python
import pytest
from datetime import datetime
from src.detection.hard_boundary import HardBoundaryDetector
from src.models.sensor import SensorData, SensorType
from src.models.anomaly import Severity, DetectionSource


class TestHardBoundaryDetector:
    @pytest.fixture
    def detector(self):
        return HardBoundaryDetector()

    @pytest.fixture
    def config(self):
        return {"hard_min": 0.0, "hard_max": 100.0}

    async def test_normal_value_no_alert(self, detector, config):
        detector.configure("temp-01", **config)
        data = SensorData(device_id="d1", sensor_id="temp-01",
                          sensor_type=SensorType.TEMPERATURE, value=50.0,
                          timestamp=datetime.now())
        result = await detector.detect(data, [])
        assert result is None

    async def test_above_max_triggers_critical(self, detector, config):
        detector.configure("temp-01", **config)
        data = SensorData(device_id="d1", sensor_id="temp-01",
                          sensor_type=SensorType.TEMPERATURE, value=150.0,
                          timestamp=datetime.now())
        result = await detector.detect(data, [])
        assert result is not None
        assert result.severity == Severity.CRITICAL
        assert result.detection_source == DetectionSource.HARD_BOUNDARY
        assert result.anomaly_score == 1.0

    async def test_below_min_triggers_critical(self, detector, config):
        detector.configure("temp-01", **config)
        data = SensorData(device_id="d1", sensor_id="temp-01",
                          sensor_type=SensorType.TEMPERATURE, value=-10.0,
                          timestamp=datetime.now())
        result = await detector.detect(data, [])
        assert result is not None
        assert result.severity == Severity.CRITICAL

    async def test_unconfigured_sensor_returns_none(self, detector):
        data = SensorData(device_id="d1", sensor_id="no-config",
                          sensor_type=SensorType.TEMPERATURE, value=50.0,
                          timestamp=datetime.now())
        result = await detector.detect(data, [])
        assert result is None

    async def test_boundary_edge_values(self, detector, config):
        detector.configure("temp-01", **config)
        at_min = SensorData(device_id="d1", sensor_id="temp-01",
                            sensor_type=SensorType.TEMPERATURE, value=0.0,
                            timestamp=datetime.now())
        at_max = SensorData(device_id="d1", sensor_id="temp-01",
                            sensor_type=SensorType.TEMPERATURE, value=100.0,
                            timestamp=datetime.now())
        assert await detector.detect(at_min, []) is None
        assert await detector.detect(at_max, []) is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_hard_boundary.py -v
```

Expected: all tests FAIL with ImportError

- [ ] **Step 3: Implement — src/detection/hard_boundary.py**

```python
import logging
from collections.abc import Sequence
from src.detection.base import Detector
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent, Severity, DetectionSource

logger = logging.getLogger(__name__)


class HardBoundaryDetector(Detector):
    def __init__(self):
        super().__init__("hard_boundary")
        self._bounds: dict[str, tuple[float, float]] = {}

    def configure(self, sensor_id: str, hard_min: float | None = None,
                  hard_max: float | None = None, **kwargs) -> None:
        if hard_min is not None and hard_max is not None:
            self._bounds[sensor_id] = (hard_min, hard_max)
            logger.info("configured %s: [%s, %s]", sensor_id, hard_min, hard_max)
        elif sensor_id in self._bounds:
            del self._bounds[sensor_id]

    async def detect(self, data: SensorData,
                     history: Sequence[SensorData]) -> AnomalyEvent | None:
        bounds = self._bounds.get(data.sensor_id)
        if bounds is None:
            return None
        lo, hi = bounds
        if lo <= data.value <= hi:
            return None
        return AnomalyEvent(
            device_id=data.device_id,
            sensor_id=data.sensor_id,
            sensor_type=data.sensor_type.value,
            timestamp=data.timestamp,
            anomaly_score=1.0,
            severity=Severity.CRITICAL,
            detection_source=DetectionSource.HARD_BOUNDARY,
            evidence={"value": data.value, "min": lo, "max": hi},
        )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_hard_boundary.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/detection/hard_boundary.py tests/test_hard_boundary.py
git commit -m "feat: add hard boundary detector"
```

---

### Task 5: Statistical Rules Detector

**Files:**
- Create: `src/detection/statistical.py`
- Test: `tests/test_statistical.py`

- [ ] **Step 1: Write failing tests — tests/test_statistical.py**

```python
import pytest
import math
from datetime import datetime, timedelta
from src.detection.statistical import StatisticalDetector
from src.models.sensor import SensorData, SensorType
from src.models.anomaly import Severity, DetectionSource
from tests.conftest import make_history


class TestStatisticalDetector:
    @pytest.fixture
    def detector(self):
        return StatisticalDetector(window_size=50, sigma=3.0)

    async def test_stable_values_no_alert(self, detector):
        history = make_history(base_value=25.0, count=100, noise=0.5)
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=25.3,
                          timestamp=datetime.now())
        result = await detector.detect(data, history)
        assert result is None

    async def test_spike_triggers_alert(self, detector):
        history = make_history(base_value=25.0, count=100, noise=0.3)
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=50.0,
                          timestamp=datetime.now())
        result = await detector.detect(data, history)
        assert result is not None
        assert result.detection_source == DetectionSource.STATISTICAL
        assert result.anomaly_score > 0.5

    async def test_insufficient_history_returns_none(self, detector):
        history = make_history(base_value=25.0, count=5, noise=0.5)
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=50.0,
                          timestamp=datetime.now())
        result = await detector.detect(data, history)
        assert result is None

    async def test_rate_of_change_detection(self, detector):
        now = datetime.now()
        history = [
            SensorData(device_id="d1", sensor_id="t1",
                       sensor_type=SensorType.TEMPERATURE, value=25.0,
                       timestamp=now - timedelta(seconds=2)),
            SensorData(device_id="d1", sensor_id="t1",
                       sensor_type=SensorType.TEMPERATURE, value=25.1,
                       timestamp=now - timedelta(seconds=1)),
        ]
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=80.0,
                          timestamp=now)
        result = await detector.detect(data, history)
        assert result is not None

    async def test_edge_case_near_boundary(self, detector):
        history = make_history(base_value=25.0, count=100, noise=0.5)
        mean = sum(h.value for h in history) / len(history)
        std = math.sqrt(sum((h.value - mean)**2 for h in history) / len(history))
        near_3sigma = mean + 2.9 * std
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=near_3sigma,
                          timestamp=datetime.now())
        result = await detector.detect(data, history)
        assert result is None
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_statistical.py -v
```

Expected: all tests FAIL with ImportError

- [ ] **Step 3: Implement — src/detection/statistical.py**

```python
import math
import logging
from collections.abc import Sequence
from src.detection.base import Detector
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent, Severity, DetectionSource

logger = logging.getLogger(__name__)


class StatisticalDetector(Detector):
    def __init__(self, window_size: int = 100, sigma: float = 3.0,
                 max_rate_of_change: float | None = None):
        super().__init__("statistical")
        self.window_size = window_size
        self.sigma = sigma
        self.max_rate_of_change = max_rate_of_change

    def configure(self, **kwargs) -> None:
        if "window_size" in kwargs:
            self.window_size = int(kwargs["window_size"])
        if "sigma" in kwargs:
            self.sigma = float(kwargs["sigma"])
        if "max_rate_of_change" in kwargs:
            self.max_rate_of_change = float(kwargs["max_rate_of_change"])

    async def detect(self, data: SensorData,
                     history: Sequence[SensorData]) -> AnomalyEvent | None:
        relevant = [h for h in history if h.sensor_id == data.sensor_id]
        if len(relevant) < self.window_size // 2:
            return None

        window = relevant[-self.window_size:]
        values = [h.value for h in window]
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std = math.sqrt(variance) if variance > 0 else 1e-9

        z_score = abs(data.value - mean) / std
        sigma_score = min(z_score / self.sigma, 1.0)

        # Rate-of-change check
        roc_violation = False
        if self.max_rate_of_change is not None and len(relevant) >= 2:
            prev = relevant[-1]
            dt = (data.timestamp - prev.timestamp).total_seconds()
            if dt > 0:
                roc = abs(data.value - prev.value) / dt
                if roc > self.max_rate_of_change:
                    roc_violation = True

        if z_score < self.sigma and not roc_violation:
            return None

        severity = Severity.WARNING
        if z_score > self.sigma * 2:
            severity = Severity.CRITICAL

        return AnomalyEvent(
            device_id=data.device_id,
            sensor_id=data.sensor_id,
            sensor_type=data.sensor_type.value,
            timestamp=data.timestamp,
            anomaly_score=round(sigma_score, 4),
            severity=severity,
            detection_source=DetectionSource.STATISTICAL,
            evidence={
                "value": data.value,
                "mean": round(mean, 4),
                "std": round(std, 4),
                "z_score": round(z_score, 4),
                "sigma": self.sigma,
                "window_size": n,
                "roc_violation": roc_violation,
            },
        )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_statistical.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/detection/statistical.py tests/test_statistical.py
git commit -m "feat: add statistical rules detector"
```

---

### Task 6: Detection Engine (Orchestrator)

**Files:**
- Create: `src/detection/engine.py`
- Test: `tests/test_detection_engine.py`

- [ ] **Step 1: Write failing test — tests/test_detection_engine.py**

```python
import pytest
from datetime import datetime, timedelta
from src.detection.engine import DetectionEngine
from src.detection.hard_boundary import HardBoundaryDetector
from src.detection.statistical import StatisticalDetector
from src.models.sensor import SensorData, SensorType
from src.models.anomaly import Severity
from tests.conftest import make_history


class TestDetectionEngine:
    @pytest.fixture
    def engine(self):
        hb = HardBoundaryDetector()
        hb.configure("t1", hard_min=0, hard_max=100)
        st = StatisticalDetector(window_size=50, sigma=3.0)
        return DetectionEngine(detectors=[hb, st])

    async def test_normal_data_no_alerts(self, engine):
        history = make_history(base_value=25.0, count=100, noise=0.3)
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=25.5,
                          timestamp=datetime.now())
        results = await engine.run(data, history)
        assert results == []

    async def test_hard_boundary_violation(self, engine):
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=150.0,
                          timestamp=datetime.now())
        results = await engine.run(data, [])
        assert len(results) == 1
        assert results[0].severity == Severity.CRITICAL

    async def test_multiple_detectors_can_trigger(self, engine):
        history = make_history(base_value=25.0, count=100, noise=0.3)
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=200.0,
                          timestamp=datetime.now())
        results = await engine.run(data, history)
        assert len(results) >= 1

    async def test_no_detectors_configured(self):
        engine = DetectionEngine(detectors=[])
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=25.0,
                          timestamp=datetime.now())
        results = await engine.run(data, [])
        assert results == []
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_detection_engine.py -v
```

Expected: all FAIL with ImportError

- [ ] **Step 3: Implement — src/detection/engine.py**

```python
import logging
from collections import defaultdict
from collections.abc import Sequence
from src.detection.base import Detector
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent

logger = logging.getLogger(__name__)


class DetectionEngine:
    def __init__(self, detectors: list[Detector] | None = None):
        self.detectors: list[Detector] = detectors or []
        self._history: dict[str, list[SensorData]] = defaultdict(list)
        self._max_history = 10_000

    def add_detector(self, detector: Detector) -> None:
        self.detectors.append(detector)
        logger.info("detector added: %s", detector.name)

    def remove_detector(self, name: str) -> bool:
        before = len(self.detectors)
        self.detectors = [d for d in self.detectors if d.name != name]
        return len(self.detectors) < before

    async def run(self, data: SensorData,
                  history: Sequence[SensorData] | None = None) -> list[AnomalyEvent]:
        key = f"{data.device_id}:{data.sensor_id}"
        if history:
            self._history[key].extend(history)
        self._history[key].append(data)

        if len(self._history[key]) > self._max_history:
            self._history[key] = self._history[key][-self._max_history:]

        full_history = self._history[key]
        events: list[AnomalyEvent] = []

        for detector in self.detectors:
            try:
                event = await detector.detect(data, full_history)
                if event is not None:
                    events.append(event)
            except Exception:
                logger.exception("detector %s failed for %s/%s",
                                 detector.name, data.device_id, data.sensor_id)

        return events

    def get_history(self, device_id: str, sensor_id: str) -> list[SensorData]:
        return self._history.get(f"{device_id}:{sensor_id}", [])
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_detection_engine.py -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/detection/engine.py tests/test_detection_engine.py
git commit -m "feat: add detection engine orchestrator"
```

---

### Task 7: Alert Deduplication

**Files:**
- Create: `src/alerting/__init__.py`
- Create: `src/alerting/dedup.py`
- Test: `tests/test_dedup.py`

- [ ] **Step 1: Write failing test — tests/test_dedup.py**

```python
import pytest
from datetime import datetime, timedelta
from src.alerting.dedup import AlertDeduplicator
from src.models.anomaly import AnomalyEvent, Severity, DetectionSource


class TestAlertDeduplicator:
    @pytest.fixture
    def dedup(self):
        return AlertDeduplicator(cooldown_seconds=300)

    def make_event(self, device_id="d1", sensor_id="s1",
                   timestamp=None, score=0.9):
        return AnomalyEvent(
            device_id=device_id, sensor_id=sensor_id,
            sensor_type="temperature",
            timestamp=timestamp or datetime.now(),
            anomaly_score=score, severity=Severity.WARNING,
            detection_source=DetectionSource.STATISTICAL,
        )

    def test_first_event_not_duplicate(self, dedup):
        event = self.make_event()
        assert not dedup.is_duplicate(event)

    def test_repeat_within_cooldown_is_duplicate(self, dedup):
        t = datetime.now()
        e1 = self.make_event(timestamp=t)
        dedup.record(e1)
        e2 = self.make_event(timestamp=t + timedelta(seconds=60))
        assert dedup.is_duplicate(e2)

    def test_repeat_after_cooldown_not_duplicate(self, dedup):
        t = datetime.now()
        e1 = self.make_event(timestamp=t)
        dedup.record(e1)
        e2 = self.make_event(timestamp=t + timedelta(seconds=301))
        assert not dedup.is_duplicate(e2)

    def test_different_sensors_not_duplicate(self, dedup):
        e1 = self.make_event(sensor_id="s1")
        dedup.record(e1)
        e2 = self.make_event(sensor_id="s2")
        assert not dedup.is_duplicate(e2)

    def test_higher_severity_overrides_cooldown(self, dedup):
        t = datetime.now()
        e1 = self.make_event(timestamp=t, severity=Severity.WARNING)
        dedup.record(e1)
        e2 = self.make_event(timestamp=t + timedelta(seconds=60),
                             severity=Severity.CRITICAL)
        assert not dedup.is_duplicate(e2)

    def test_record_updates_last_seen(self, dedup):
        t = datetime.now()
        e1 = self.make_event(timestamp=t)
        dedup.record(e1)
        key = "d1:s1"
        assert key in dedup._last_alert
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_dedup.py -v
```

Expected: all FAIL with ImportError

- [ ] **Step 3: Implement — src/alerting/dedup.py**

```python
import time
import logging
from datetime import datetime
from src.models.anomaly import AnomalyEvent, Severity

logger = logging.getLogger(__name__)


class AlertDeduplicator:
    def __init__(self, cooldown_seconds: int = 300):
        self.cooldown = cooldown_seconds
        self._last_alert: dict[str, float] = {}
        self._last_severity: dict[str, Severity] = {}

    def _key(self, event: AnomalyEvent) -> str:
        return f"{event.device_id}:{event.sensor_id}"

    def is_duplicate(self, event: AnomalyEvent) -> bool:
        key = self._key(event)
        if key not in self._last_alert:
            return False
        # Higher severity always passes through
        prev_sev = self._last_severity.get(key)
        if prev_sev and self._severity_rank(event.severity) > self._severity_rank(prev_sev):
            return False
        elapsed = time.time() - self._last_alert[key]
        return elapsed < self.cooldown

    def record(self, event: AnomalyEvent) -> None:
        key = self._key(event)
        self._last_alert[key] = time.time()
        self._last_severity[key] = event.severity
        logger.debug("recorded alert for %s at severity=%s", key, event.severity)

    @staticmethod
    def _severity_rank(sev: Severity) -> int:
        return {Severity.INFO: 0, Severity.WARNING: 1, Severity.CRITICAL: 2}[sev]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_dedup.py -v
```

Expected: 6 passed

- [ ] **Step 5: Commit**

```bash
git add src/alerting/ tests/test_dedup.py
git commit -m "feat: add alert deduplication with cooldown"
```

---

### Task 8: Alert Channels and Router

**Files:**
- Create: `src/alerting/channels.py`
- Create: `src/alerting/router.py`
- Test: `tests/test_alert_router.py`

- [ ] **Step 1: Create src/alerting/channels.py**

```python
import logging
from abc import ABC, abstractmethod
from src.models.anomaly import AnomalyEvent

logger = logging.getLogger(__name__)


class AlertChannel(ABC):
    @abstractmethod
    async def send(self, event: AnomalyEvent) -> bool:
        ...


class ConsoleChannel(AlertChannel):
    async def send(self, event: AnomalyEvent) -> bool:
        logger.warning(
            "[%s] %s/%s: %s (score=%.3f)",
            event.severity.value.upper(),
            event.device_id, event.sensor_id,
            event.detection_source.value, event.anomaly_score,
        )
        return True


class DingTalkChannel(AlertChannel):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, event: AnomalyEvent) -> bool:
        import httpx
        if not self.webhook_url:
            return False
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "msgtype": "text",
                    "text": {
                        "content": (
                            f"[{event.severity.value.upper()}] IoT Alert\n"
                            f"Device: {event.device_id}\n"
                            f"Sensor: {event.sensor_id} ({event.sensor_type})\n"
                            f"Score: {event.anomaly_score:.3f}\n"
                            f"Source: {event.detection_source.value}\n"
                            f"Time: {event.timestamp.isoformat()}"
                        )
                    }
                }
                r = await client.post(self.webhook_url, json=payload, timeout=5)
                return r.is_success
        except Exception:
            logger.exception("DingTalk send failed")
            return False


class FeishuChannel(AlertChannel):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, event: AnomalyEvent) -> bool:
        import httpx
        if not self.webhook_url:
            return False
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "msg_type": "interactive",
                    "card": {
                        "header": {
                            "title": {"tag": "plain_text",
                                      "content": f"IoT Alert - {event.severity.value.upper()}"},
                            "template": "red" if event.severity.value == "critical" else "yellow",
                        },
                        "elements": [
                            {"tag": "div", "text": {"tag": "lark_md",
                                     "content": f"**Device:** {event.device_id}\n"
                                                f"**Sensor:** {event.sensor_id}\n"
                                                f"**Score:** {event.anomaly_score:.3f}\n"
                                                f"**Time:** {event.timestamp.isoformat()}"}},
                        ]
                    }
                }
                r = await client.post(self.webhook_url, json=payload, timeout=5)
                return r.is_success
        except Exception:
            logger.exception("Feishu send failed")
            return False
```

- [ ] **Step 2: Create src/alerting/router.py**

```python
import logging
from src.alerting.dedup import AlertDeduplicator
from src.alerting.channels import AlertChannel, ConsoleChannel
from src.models.anomaly import AnomalyEvent, Severity

logger = logging.getLogger(__name__)


class AlertRouter:
    def __init__(self, dedup: AlertDeduplicator | None = None):
        self.dedup = dedup or AlertDeduplicator()
        self._channels: dict[Severity, list[AlertChannel]] = {
            Severity.CRITICAL: [ConsoleChannel()],
            Severity.WARNING: [ConsoleChannel()],
            Severity.INFO: [ConsoleChannel()],
        }

    def add_channel(self, severity: Severity, channel: AlertChannel) -> None:
        self._channels.setdefault(severity, []).append(channel)

    async def route(self, event: AnomalyEvent) -> bool:
        if self.dedup.is_duplicate(event):
            logger.debug("dedup suppressed: %s/%s", event.device_id, event.sensor_id)
            return False
        self.dedup.record(event)
        channels = self._channels.get(event.severity, [])
        results = []
        for ch in channels:
            try:
                ok = await ch.send(event)
                results.append(ok)
            except Exception:
                logger.exception("channel %s failed", type(ch).__name__)
                results.append(False)
        return any(results)
```

- [ ] **Step 3: Write test — tests/test_alert_router.py**

```python
import pytest
from datetime import datetime
from src.alerting.router import AlertRouter
from src.alerting.channels import ConsoleChannel
from src.models.anomaly import AnomalyEvent, Severity, DetectionSource


class TestAlertRouter:
    @pytest.fixture
    def router(self):
        return AlertRouter()

    def make_event(self, severity=Severity.WARNING, device="d1", sensor="s1"):
        return AnomalyEvent(
            device_id=device, sensor_id=sensor,
            sensor_type="temperature",
            timestamp=datetime.now(),
            anomaly_score=0.9, severity=severity,
            detection_source=DetectionSource.STATISTICAL,
        )

    async def test_routes_event_to_channel(self, router):
        event = self.make_event()
        result = await router.route(event)
        assert result is True

    async def test_dedup_blocks_repeat(self, router):
        e1 = self.make_event()
        await router.route(e1)
        e2 = self.make_event()
        result = await router.route(e2)
        assert result is False
```

- [ ] **Step 4: Run tests**

```bash
python -m pytest tests/test_alert_router.py -v
```

Expected: 2 passed

- [ ] **Step 5: Commit**

```bash
git add src/alerting/router.py src/alerting/channels.py tests/test_alert_router.py
git commit -m "feat: add alert channels and router"
```

---

### Task 9: POT Dynamic Threshold

**Files:**
- Create: `src/threshold/__init__.py`
- Create: `src/threshold/pot.py`
- Test: `tests/test_pot.py`

- [ ] **Step 1: Write failing test — tests/test_pot.py**

```python
import pytest
import random
from src.threshold.pot import POTThreshold


class TestPOTThreshold:
    @pytest.fixture
    def pot(self):
        return POTThreshold(alpha=0.01, window=500)

    def test_initial_threshold_is_infinite(self, pot):
        assert pot.threshold == float("inf")

    def test_fit_sets_threshold(self, pot):
        random.seed(42)
        data = [random.gauss(0, 1) for _ in range(600)]
        pot.update_batch(data)
        assert pot.threshold > 0
        assert pot.threshold < float("inf")

    def test_threshold_adapts_to_larger_values(self, pot):
        random.seed(42)
        normal = [abs(random.gauss(0, 1)) for _ in range(500)]
        pot.update_batch(normal)
        t1 = pot.threshold
        large = [abs(random.gauss(5, 1)) for _ in range(1000)]
        pot.update_batch(large)
        t2 = pot.threshold
        assert t2 > t1

    def test_is_anomaly(self, pot):
        random.seed(42)
        data = [abs(random.gauss(0, 1)) for _ in range(600)]
        pot.update_batch(data)
        assert not pot.is_anomaly(0.5)
        assert pot.is_anomaly(pot.threshold * 3)

    def test_shorter_than_initial_data(self, pot):
        data = [1.0, 2.0, 3.0]
        pot.update_batch(data)
        assert pot.threshold == float("inf")
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_pot.py -v
```

Expected: all FAIL with ImportError

- [ ] **Step 3: Implement — src/threshold/pot.py**

```python
import math
import logging
from collections import deque

logger = logging.getLogger(__name__)


class POTThreshold:
    """Peak-Over-Threshold: fits GPD to tail of error distribution."""

    def __init__(self, alpha: float = 0.001, window: int = 1000,
                 initial_quantile: float = 0.98):
        self.alpha = alpha
        self.window = window
        self.initial_quantile = initial_quantile
        self._buffer: deque[float] = deque(maxlen=window)
        self._threshold: float = float("inf")
        self._params: tuple[float, float] | None = None
        self._n_below_init: int = 0

    @property
    def threshold(self) -> float:
        return self._threshold

    def update(self, value: float) -> None:
        self._buffer.append(value)
        if len(self._buffer) >= self.window // 2:
            self._refit()

    def update_batch(self, values: list[float]) -> None:
        for v in values:
            self._buffer.append(v)
        if len(self._buffer) >= self.window // 2:
            self._refit()

    def is_anomaly(self, value: float) -> bool:
        return value > self._threshold

    def _refit(self) -> None:
        data = sorted(self._buffer)
        n = len(data)
        if n < 100:
            return
        # Use upper quantile as threshold for GPD fit
        t_index = int(n * self.initial_quantile)
        t = data[t_index]
        excesses = [x - t for x in data if x > t]
        if len(excesses) < 10:
            # Fallback: use empirical quantile
            self._threshold = data[int(n * (1 - self.alpha))]
            return
        # Fit GPD via MLE (approximation via method of moments)
        excess_mean = sum(excesses) / len(excesses)
        excess_var = sum((x - excess_mean) ** 2 for x in excesses) / len(excesses)
        if excess_var < 1e-9 or excess_mean < 1e-9:
            self._threshold = data[int(n * (1 - self.alpha))]
            return
        shape = 0.5 * ((excess_mean ** 2 / excess_var) - 1)
        scale = 0.5 * excess_mean * ((excess_mean ** 2 / excess_var) + 1)

        # z_q = t + (scale/shape) * (( (n/Nt * alpha)^(-shape) ) - 1)
        Nt = len(excesses)
        try:
            z_q = t + (scale / shape) * (((n / Nt) * self.alpha) ** (-shape) - 1)
            if z_q > t and not math.isnan(z_q) and not math.isinf(z_q):
                self._threshold = z_q
                self._params = (shape, scale)
            else:
                self._threshold = data[int(n * (1 - self.alpha))]
        except (OverflowError, ValueError, ZeroDivisionError):
            self._threshold = data[int(n * (1 - self.alpha))]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_pot.py -v
```

Expected: 5 passed

- [ ] **Step 5: Commit**

```bash
git add src/threshold/ tests/test_pot.py
git commit -m "feat: add POT dynamic threshold"
```

---

### Task 10: RobustScaler Preprocessing

**Files:**
- Create: `src/preprocessing/__init__.py`
- Create: `src/preprocessing/scaler.py`
- Test: `tests/test_scaler.py`

- [ ] **Step 1: Write failing test — tests/test_scaler.py**

```python
import pytest
import numpy as np
from src.preprocessing.scaler import RobustScaler


class TestRobustScaler:
    @pytest.fixture
    def scaler(self):
        return RobustScaler()

    def test_fit_transform_centers_on_median(self, scaler):
        data = np.array([1.0, 2.0, 3.0, 4.0, 100.0])  # outlier at end
        scaler.fit(data)
        transformed = scaler.transform(data)
        assert abs(np.median(transformed)) < 1.0

    def test_outlier_resistant(self, scaler):
        data = np.array([10.0, 11.0, 9.0, 10.5, 10.2, 500.0])
        scaler.fit(data)
        transformed = scaler.transform(data)
        # The 500.0 should still be large but not dominate normalization
        assert transformed[-1] > 3.0

    def test_fit_multiple_sensors(self, scaler):
        sensor_data = {
            "temp": np.array([20.0, 21.0, 19.0, 22.0, 20.5]),
            "vib": np.array([0.1, 0.12, 0.09, 0.11, 0.1]),
        }
        scaler.fit_multi(sensor_data)
        result = scaler.transform_multi(sensor_data)
        for key in sensor_data:
            assert result[key].shape == sensor_data[key].shape
            assert abs(np.median(result[key])) < 0.5

    def test_inverse_transform(self, scaler):
        data = np.array([10.0, 20.0, 30.0])
        scaler.fit(data)
        transformed = scaler.transform(data)
        restored = scaler.inverse_transform(transformed)
        np.testing.assert_array_almost_equal(restored, data)
```

- [ ] **Step 2: Run test to verify it fails**

```bash
python -m pytest tests/test_scaler.py -v
```

Expected: all FAIL with ImportError

- [ ] **Step 3: Implement — src/preprocessing/scaler.py**

```python
import numpy as np


class RobustScaler:
    """Median + IQR based scaler, resistant to outliers."""

    def __init__(self, with_centering: bool = True, with_scaling: bool = True):
        self.with_centering = with_centering
        self.with_scaling = with_scaling
        self._medians: dict[str, float] = {}
        self._iqrs: dict[str, float] = {}

    def fit(self, data: np.ndarray) -> "RobustScaler":
        q1, med, q3 = np.percentile(data, [25, 50, 75])
        self._medians["_default"] = med
        self._iqrs["_default"] = q3 - q1 if q3 > q1 else 1.0
        return self

    def transform(self, data: np.ndarray) -> np.ndarray:
        med = self._medians.get("_default", 0.0)
        iqr = self._iqrs.get("_default", 1.0)
        result = data.astype(np.float64).copy()
        if self.with_centering:
            result -= med
        if self.with_scaling and iqr > 1e-9:
            result /= iqr
        return result

    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        med = self._medians.get("_default", 0.0)
        iqr = self._iqrs.get("_default", 1.0)
        result = data.astype(np.float64).copy()
        if self.with_scaling and iqr > 1e-9:
            result *= iqr
        if self.with_centering:
            result += med
        return result

    def fit_multi(self, sensor_data: dict[str, np.ndarray]) -> "RobustScaler":
        for key, arr in sensor_data.items():
            q1, med, q3 = np.percentile(arr, [25, 50, 75])
            self._medians[key] = med
            self._iqrs[key] = q3 - q1 if q3 > q1 else 1.0
        return self

    def transform_multi(self, sensor_data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        result = {}
        for key, arr in sensor_data.items():
            med = self._medians.get(key, 0.0)
            iqr = self._iqrs.get(key, 1.0)
            transformed = arr.astype(np.float64).copy()
            if self.with_centering:
                transformed -= med
            if self.with_scaling and iqr > 1e-9:
                transformed /= iqr
            result[key] = transformed
        return result
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest tests/test_scaler.py -v
```

Expected: 4 passed

- [ ] **Step 5: Commit**

```bash
git add src/preprocessing/ tests/test_scaler.py
git commit -m "feat: add RobustScaler preprocessing"
```

---

### Task 11: Storage Layer (PostgreSQL, TimescaleDB, Redis)

**Files:**
- Create: `src/storage/__init__.py`
- Create: `src/storage/postgres.py`
- Create: `src/storage/timescaledb.py`
- Create: `src/storage/redis.py`

- [ ] **Step 1: Create src/storage/postgres.py**

```python
import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.config import settings

logger = logging.getLogger(__name__)

engine = create_async_engine(settings.postgres_dsn, echo=False)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
```

- [ ] **Step 2: Create src/storage/timescaledb.py**

```python
import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.config import settings

logger = logging.getLogger(__name__)

timescale_engine = create_async_engine(settings.timescale_dsn, echo=False)
TimescaleSession = async_sessionmaker(timescale_engine, expire_on_commit=False)


async def init_timescaledb() -> None:
    async with timescale_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                time TIMESTAMPTZ NOT NULL,
                device_id TEXT NOT NULL,
                sensor_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value DOUBLE PRECISION NOT NULL,
                unit TEXT
            )
        """))
        await conn.execute(text("""
            SELECT create_hypertable('sensor_data', 'time', if_not_exists => TRUE);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_sensor_data_device_sensor
            ON sensor_data (device_id, sensor_id, time DESC);
        """))


async def insert_sensor_data(session: AsyncSession, data) -> None:
    await session.execute(text("""
        INSERT INTO sensor_data (time, device_id, sensor_id, sensor_type, value, unit)
        VALUES (:time, :device_id, :sensor_id, :sensor_type, :value, :unit)
    """), {
        "time": data.timestamp,
        "device_id": data.device_id,
        "sensor_id": data.sensor_id,
        "sensor_type": data.sensor_type.value,
        "value": data.value,
        "unit": data.unit,
    })
    await session.commit()


async def query_sensor_history(
    device_id: str, sensor_id: str,
    start: datetime, end: datetime,
    limit: int = 10000,
) -> list[dict]:
    async with TimescaleSession() as session:
        result = await session.execute(text("""
            SELECT time, device_id, sensor_id, sensor_type, value, unit
            FROM sensor_data
            WHERE device_id = :device_id AND sensor_id = :sensor_id
              AND time >= :start AND time <= :end
            ORDER BY time DESC
            LIMIT :limit
        """), {"device_id": device_id, "sensor_id": sensor_id,
               "start": start, "end": end, "limit": limit})
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]
```

- [ ] **Step 3: Create src/storage/redis.py**

```python
import json
import logging
from redis.asyncio import Redis
from src.config import settings

logger = logging.getLogger(__name__)

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


async def cache_window(device_id: str, sensor_id: str,
                       data_points: list[dict], ttl: int = 3600) -> None:
    key = f"window:{device_id}:{sensor_id}"
    await redis_client.set(key, json.dumps(data_points, default=str), ex=ttl)


async def get_cached_window(device_id: str, sensor_id: str) -> list[dict]:
    key = f"window:{device_id}:{sensor_id}"
    raw = await redis_client.get(key)
    if raw:
        return json.loads(raw)
    return []


async def set_device_state(device_id: str, state: str) -> None:
    await redis_client.hset("device_states", device_id, state)


async def get_device_state(device_id: str) -> str | None:
    return await redis_client.hget("device_states", device_id)


async def check_rate_limit(key: str, window_seconds: int,
                           max_count: int) -> bool:
    current = await redis_client.incr(f"ratelimit:{key}")
    if current == 1:
        await redis_client.expire(f"ratelimit:{key}", window_seconds)
    return current <= max_count
```

- [ ] **Step 4: Create Docker Compose for dependencies — docker-compose.yml**

```yaml
services:
  postgres:
    image: timescale/timescaledb:latest-pg16
    environment:
      POSTGRES_USER: iot
      POSTGRES_PASSWORD: iot
      POSTGRES_DB: iot
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  emqx:
    image: emqx/emqx:latest
    ports:
      - "1883:1883"
      - "18083:18083"
    environment:
      EMQX_NAME: emqx
      EMQX_HOST: 127.0.0.1

volumes:
  pgdata:
```

- [ ] **Step 5: Commit**

```bash
git add src/storage/ docker-compose.yml
git commit -m "feat: add storage layer and docker-compose for dependencies"
```

---

### Task 12: MQTT Ingestion

**Files:**
- Create: `src/ingestion/__init__.py`
- Create: `src/ingestion/mqtt.py`

- [ ] **Step 1: Create src/ingestion/mqtt.py**

```python
import json
import logging
from datetime import datetime
from collections.abc import Callable, Awaitable
import aiomqtt
from src.config import settings
from src.models.sensor import SensorData, SensorType

logger = logging.getLogger(__name__)

Handler = Callable[[SensorData], Awaitable[None]]


class MQTTIngestor:
    def __init__(self, handler: Handler):
        self.handler = handler
        self._client: aiomqtt.Client | None = None

    async def start(self) -> None:
        while True:
            try:
                async with aiomqtt.Client(hostname=settings.mqtt_host,
                                          port=settings.mqtt_port) as client:
                    self._client = client
                    await client.subscribe(settings.mqtt_topic)
                    logger.info("MQTT connected, subscribed to %s", settings.mqtt_topic)
                    async for message in client.messages:
                        await self._handle_message(message)
            except aiomqtt.MqttError:
                logger.exception("MQTT connection lost, reconnecting in 5s...")
                import asyncio
                await asyncio.sleep(5)

    async def stop(self) -> None:
        if self._client:
            await self._client.__aexit__(None, None, None)

    async def _handle_message(self, message) -> None:
        try:
            payload = json.loads(message.payload)
            data = SensorData(
                device_id=payload["device_id"],
                sensor_id=payload["sensor_id"],
                sensor_type=SensorType(payload["sensor_type"]),
                value=float(payload["value"]),
                timestamp=datetime.fromisoformat(payload["timestamp"]),
                unit=payload.get("unit"),
            )
            await self.handler(data)
        except (json.JSONDecodeError, KeyError, ValueError):
            logger.warning("invalid MQTT message on %s: %s",
                           message.topic, message.payload[:200])
```

- [ ] **Step 2: Create sensor simulator for testing — src/cli/__init__.py, src/cli/simulate.py**

```python
# src/cli/__init__.py (empty)

# src/cli/simulate.py
import asyncio
import json
import random
import time
from datetime import datetime, timezone
import aiomqtt


async def simulate(devices: int = 5, sensors_per_device: int = 2,
                   interval: float = 1.0, host: str = "localhost",
                   port: int = 1883):
    sensor_types = ["temperature", "vibration", "current", "humidity"]
    baselines = {"temperature": 25.0, "vibration": 0.5, "current": 10.0,
                 "humidity": 50.0}
    noise = {"temperature": 1.0, "vibration": 0.05, "current": 0.3,
             "humidity": 2.0}

    async with aiomqtt.Client(hostname=host, port=port) as client:
        while True:
            for d in range(devices):
                for s in range(sensors_per_device):
                    stype = random.choice(sensor_types)
                    base = baselines[stype]
                    n = noise[stype]
                    # Inject anomaly ~2% of the time
                    if random.random() < 0.02:
                        base *= random.choice([3.0, -2.0, 5.0])
                    value = base + random.gauss(0, n)
                    payload = {
                        "device_id": f"dev-{d:03d}",
                        "sensor_id": f"{stype}-{s:02d}",
                        "sensor_type": stype,
                        "value": round(value, 4),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "unit": "",
                    }
                    await client.publish("sensors/data", json.dumps(payload))
            await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(simulate())
```

- [ ] **Step 3: Commit**

```bash
git add src/ingestion/ src/cli/
git commit -m "feat: add MQTT ingestion and sensor simulator"
```

---

### Task 13: FastAPI Application and WebSocket

**Files:**
- Create: `src/api/__init__.py`, `src/api/app.py`, `src/api/deps.py`
- Create: `src/api/routes/__init__.py`, `src/api/routes/alerts.py`,
          `src/api/routes/devices.py`, `src/api/routes/data.py`
- Create: `src/api/websocket.py`

- [ ] **Step 1: Create src/api/deps.py**

```python
from src.detection.engine import DetectionEngine
from src.alerting.router import AlertRouter

_detection_engine: DetectionEngine | None = None
_alert_router: AlertRouter | None = None


def get_engine() -> DetectionEngine:
    global _detection_engine
    if _detection_engine is None:
        from src.detection.hard_boundary import HardBoundaryDetector
        from src.detection.statistical import StatisticalDetector
        _detection_engine = DetectionEngine(
            detectors=[HardBoundaryDetector(), StatisticalDetector()]
        )
    return _detection_engine


def set_engine(engine: DetectionEngine) -> None:
    global _detection_engine
    _detection_engine = engine


def get_alert_router() -> AlertRouter:
    global _alert_router
    if _alert_router is None:
        _alert_router = AlertRouter()
    return _alert_router


def set_alert_router(router: AlertRouter) -> None:
    global _alert_router
    _alert_router = router
```

- [ ] **Step 2: Create src/api/routes/alerts.py**

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.deps import get_engine

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# In-memory store for demo; replaced by PostgreSQL in production
_alerts_store: list[dict] = []


@router.get("")
async def list_alerts(limit: int = Query(50, le=500), offset: int = 0):
    return {
        "total": len(_alerts_store),
        "items": _alerts_store[offset:offset + limit],
    }


@router.post("/{event_id}/feedback")
async def submit_feedback(event_id: str, confirmed: bool, operator: str = "anonymous"):
    for alert in _alerts_store:
        if alert["event_id"] == event_id:
            alert["status"] = "confirmed" if confirmed else "rejected"
            alert["confirmed_by"] = operator
            alert["confirmed_at"] = __import__("datetime").datetime.now().isoformat()
            return {"ok": True, "event_id": event_id}
    raise HTTPException(404, "alert not found")


def store_alert(event_dict: dict) -> None:
    _alerts_store.insert(0, event_dict)
    if len(_alerts_store) > 10000:
        _alerts_store.pop()
```

- [ ] **Step 3: Create src/api/routes/data.py**

```python
from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/sensors/{device_id}/{sensor_id}")
async def query_sensor_data(
    device_id: str,
    sensor_id: str,
    start: str,
    end: str,
    limit: int = Query(1000, le=10000),
):
    from datetime import datetime
    from src.storage.timescaledb import query_sensor_history
    try:
        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
    except ValueError:
        raise HTTPException(400, "invalid ISO datetime for start/end")
    rows = await query_sensor_history(device_id, sensor_id, s, e, limit)
    return {"device_id": device_id, "sensor_id": sensor_id, "count": len(rows),
            "data": rows}
```

- [ ] **Step 4: Create src/api/websocket.py**

```python
import json
import logging
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class AlertBroadcaster:
    def __init__(self):
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)

    def disconnect(self, ws: WebSocket) -> None:
        if ws in self._connections:
            self._connections.remove(ws)

    async def broadcast(self, event_dict: dict) -> None:
        payload = json.dumps(event_dict, default=str)
        stale = []
        for ws in self._connections:
            try:
                await ws.send_text(payload)
            except Exception:
                stale.append(ws)
        for ws in stale:
            self._connections.remove(ws)


broadcaster = AlertBroadcaster()
```

- [ ] **Step 5: Create src/api/app.py**

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import alerts, data, devices
from src.api.websocket import broadcaster
from src.api.deps import get_engine, get_alert_router
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent
from src.storage.timescaledb import TimescaleSession, insert_sensor_data
from src.api.routes.alerts import store_alert
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.storage.postgres import init_db
    from src.storage.timescaledb import init_timescaledb
    await init_db()
    await init_timescaledb()
    logger.info("database initialized")
    yield


app = FastAPI(title="IoT Anomaly Detection", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(alerts.router)
app.include_router(data.router)
app.include_router(devices.router)


@app.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket):
    await broadcaster.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)


@app.post("/api/ingest")
async def ingest(data: SensorData):
    engine = get_engine()
    events: list[AnomalyEvent] = await engine.run(data)

    # Store to TimescaleDB
    async with TimescaleSession() as session:
        await insert_sensor_data(session, data)

    router = get_alert_router()
    for event in events:
        event_dict = event.model_dump()
        store_alert(event_dict)
        await router.route(event)
        await broadcaster.broadcast(event_dict)

    return {"received": True, "anomalies": len(events)}
```

- [ ] **Step 6: Create src/api/routes/devices.py**

```python
from fastapi import APIRouter
from src.api.deps import get_engine

router = APIRouter(prefix="/api/devices", tags=["devices"])

_devices: dict[str, dict] = {}


@router.get("")
async def list_devices():
    return {"total": len(_devices), "items": list(_devices.values())}


@router.post("/{device_id}/sensors/{sensor_id}/config")
async def configure_sensor(device_id: str, sensor_id: str,
                           hard_min: float | None = None,
                           hard_max: float | None = None):
    engine = get_engine()
    for detector in engine.detectors:
        if detector.name == "hard_boundary":
            detector.configure(sensor_id, hard_min=hard_min, hard_max=hard_max)
            return {"ok": True, "device_id": device_id, "sensor_id": sensor_id}
    return {"ok": False, "error": "hard_boundary detector not found"}
```

- [ ] **Step 7: Write integration test — tests/test_api.py**

```python
import pytest
from datetime import datetime, timezone
from httpx import AsyncClient, ASGITransport
from src.api.app import app
from src.models.sensor import SensorData, SensorType


class TestAPI:
    @pytest.fixture
    async def client(self):
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

    async def test_ingest_normal_data(self, client):
        payload = {
            "device_id": "d1", "sensor_id": "t1",
            "sensor_type": "temperature", "value": 25.0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        r = await client.post("/api/ingest", json=payload)
        assert r.status_code == 200
        assert r.json()["received"] is True

    async def test_ingest_anomalous_data(self, client):
        # Send history to establish baseline
        for i in range(100):
            payload = {
                "device_id": "d2", "sensor_id": "t2",
                "sensor_type": "temperature",
                "value": 25.0 + (i % 3) * 0.1,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
            await client.post("/api/ingest", json=payload)

        # Send an anomaly spike
        payload["value"] = 100.0
        r = await client.post("/api/ingest", json=payload)
        assert r.status_code == 200
        assert r.json()["anomalies"] >= 1

    async def test_list_alerts(self, client):
        r = await client.get("/api/alerts")
        assert r.status_code == 200
        assert "items" in r.json()
```

- [ ] **Step 8: Run API tests**

```bash
python -m pytest tests/test_api.py -v
```

Expected: 3 passed

- [ ] **Step 9: Commit**

```bash
git add src/api/ tests/test_api.py
git commit -m "feat: add FastAPI application with WebSocket and routes"
```

---

### Task 14: Main Entrypoint

**Files:**
- Modify: `main.py`
- Create: `Dockerfile`

- [ ] **Step 1: Update main.py**

```python
import asyncio
import logging
from src.config import settings
from src.api.app import app
from src.api.deps import set_engine, set_alert_router
from src.ingestion.mqtt import MQTTIngestor
from src.detection.engine import DetectionEngine
from src.detection.hard_boundary import HardBoundaryDetector
from src.detection.statistical import StatisticalDetector
from src.alerting.router import AlertRouter
from src.alerting.channels import ConsoleChannel
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent
from src.storage.timescaledb import TimescaleSession, insert_sensor_data
from src.api.routes.alerts import store_alert
from src.api.websocket import broadcaster

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def handle_sensor_data(data: SensorData) -> None:
    from src.api.deps import get_engine, get_alert_router
    engine = get_engine()
    events: list[AnomalyEvent] = await engine.run(data)

    async with TimescaleSession() as session:
        await insert_sensor_data(session, data)

    router = get_alert_router()
    for event in events:
        event_dict = event.model_dump()
        store_alert(event_dict)
        await router.route(event)
        await broadcaster.broadcast(event_dict)


def main():
    # Init detectors — creates engine with default detectors
    from src.api.deps import get_engine, get_alert_router
    engine = get_engine()
    router = get_alert_router()
    from src.models.anomaly import Severity
    router.add_channel(Severity.CRITICAL, ConsoleChannel())
    router.add_channel(Severity.WARNING, ConsoleChannel())

    ingestor = MQTTIngestor(handler=handle_sensor_data)

    import uvicorn
    import threading

    def run_api():
        uvicorn.run(app, host=settings.api_host, port=settings.api_port)

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    logger.info("API server starting on %s:%s", settings.api_host, settings.api_port)

    asyncio.run(ingestor.start())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Create Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[dev]" && pip install uvicorn
COPY src/ src/
COPY main.py .

EXPOSE 8000
CMD ["python", "main.py"]
```

- [ ] **Step 3: Verify the app can import**

```bash
python -c "from src.api.app import app; print('FastAPI app OK')"
```

Expected: prints "FastAPI app OK"

- [ ] **Step 4: Commit**

```bash
git add main.py Dockerfile
git commit -m "feat: add main entrypoint and Dockerfile"
```

---

### Task 15: LSTM-Autoencoder Model (Phase 2)

**Files:**
- Create: `src/training/__init__.py`
- Create: `src/training/model.py`
- Create: `src/training/dataset.py`
- Create: `src/training/train.py`
- Create: `src/training/self_cleaning.py`
- Create: `src/training/export_onnx.py`
- Create: `src/detection/lstm_ae.py`
- Test: `tests/test_lstm_ae_model.py`, `tests/test_training.py`

- [ ] **Step 1: Create src/training/model.py**

```python
import torch
import torch.nn as nn


class LSTMAutoencoder(nn.Module):
    def __init__(self, n_sensors: int, hidden_dim: int = 64,
                 num_layers: int = 2, dropout: float = 0.2,
                 window_size: int = 128):
        super().__init__()
        self.n_sensors = n_sensors
        self.hidden_dim = hidden_dim
        self.window_size = window_size

        self.encoder = nn.LSTM(
            input_size=n_sensors, hidden_size=hidden_dim,
            num_layers=num_layers, batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
            bidirectional=True,
        )
        self.enc_proj = nn.Linear(hidden_dim * 2, hidden_dim)

        self.decoder = nn.LSTM(
            input_size=hidden_dim, hidden_size=hidden_dim,
            num_layers=num_layers, batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0,
        )
        self.output_layer = nn.Linear(hidden_dim, n_sensors)

    def forward(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        # x: (batch, window_size, n_sensors)
        batch_size = x.size(0)

        # Encode
        enc_out, (h_n, c_n) = self.encoder(x)
        # Use last hidden state from both directions
        h_forward = h_n[-2:, :, :]  # last 2 layers forward
        h_backward = h_n[-2:, :, :]  # last 2 layers backward
        h_cat = torch.cat([h_forward[-1], h_backward[-1]], dim=-1)
        z = self.enc_proj(h_cat)  # (batch, hidden_dim)

        # Decode: repeat z for each time step
        z_repeated = z.unsqueeze(1).repeat(1, self.window_size, 1)
        dec_out, _ = self.decoder(z_repeated)
        reconstruction = self.output_layer(dec_out)

        return reconstruction, z


def reconstruction_error(x: torch.Tensor, x_hat: torch.Tensor,
                         per_sensor: bool = True) -> torch.Tensor:
    """MSE per sensor (batch, n_sensors) or global."""
    se = (x - x_hat) ** 2
    if per_sensor:
        return se.mean(dim=1)  # (batch, n_sensors)
    return se.mean(dim=[1, 2])  # (batch,)
```

- [ ] **Step 2: Create src/training/dataset.py**

```python
import numpy as np
import torch
from torch.utils.data import Dataset


class SlidingWindowDataset(Dataset):
    def __init__(self, data: np.ndarray, window_size: int = 128,
                 stride: int = 32):
        # data: (n_timesteps, n_sensors)
        self.data = torch.FloatTensor(data)
        self.window_size = window_size
        self.stride = stride
        n_windows = max(0, (len(data) - window_size) // stride + 1)
        self._indices = [i * stride for i in range(n_windows)]

    def __len__(self) -> int:
        return len(self._indices)

    def __getitem__(self, idx: int) -> torch.Tensor:
        start = self._indices[idx]
        return self.data[start:start + self.window_size]
```

- [ ] **Step 3: Create src/training/train.py**

```python
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from src.training.model import LSTMAutoencoder, reconstruction_error
from src.training.dataset import SlidingWindowDataset
import logging

logger = logging.getLogger(__name__)


def train_model(data: np.ndarray, n_sensors: int, hidden_dim: int = 64,
                window_size: int = 128, epochs: int = 50,
                batch_size: int = 64, lr: float = 0.001,
                patience: int = 10, device: str = "cpu") -> LSTMAutoencoder:
    model = LSTMAutoencoder(n_sensors=n_sensors, hidden_dim=hidden_dim,
                            window_size=window_size).to(device)
    dataset = SlidingWindowDataset(data, window_size=window_size, stride=32)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.MSELoss()

    best_loss = float("inf")
    patience_counter = 0

    for epoch in range(epochs):
        model.train()
        total_loss = 0.0
        for batch in loader:
            batch = batch.to(device)
            optimizer.zero_grad()
            recon, _ = model(batch)
            loss = criterion(recon, batch)
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            total_loss += loss.item()

        avg_loss = total_loss / len(loader)
        logger.info("epoch %d/%d loss=%.6f", epoch + 1, epochs, avg_loss)

        if avg_loss < best_loss * 0.999:
            best_loss = avg_loss
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                logger.info("early stopping at epoch %d", epoch + 1)
                break

    return model
```

- [ ] **Step 4: Create src/training/self_cleaning.py**

```python
import numpy as np
import torch
from torch.utils.data import DataLoader
from src.training.model import LSTMAutoencoder, reconstruction_error
from src.training.dataset import SlidingWindowDataset
from src.training.train import train_model
import logging

logger = logging.getLogger(__name__)


def self_cleaning_train(data: np.ndarray, n_sensors: int,
                        hidden_dim: int = 64, window_size: int = 128,
                        clean_fraction: float = 0.05, device: str = "cpu",
                        **train_kwargs) -> LSTMAutoencoder:
    # Round 1: train on all data
    logger.info("self-cleaning round 1: training on full data (%d points)", len(data))
    model = train_model(data, n_sensors, hidden_dim, window_size,
                        device=device, **train_kwargs)

    # Score all windows
    model.eval()
    dataset = SlidingWindowDataset(data, window_size=window_size, stride=32)
    loader = DataLoader(dataset, batch_size=64)
    errors = []
    with torch.no_grad():
        for batch in loader:
            batch = batch.to(device)
            recon, _ = model(batch)
            err = reconstruction_error(batch, recon, per_sensor=False)
            errors.extend(err.cpu().numpy().tolist())

    # Remove top clean_fraction windows
    threshold = np.percentile(errors, (1 - clean_fraction) * 100)
    keep_mask = np.array(errors) <= threshold
    keep_indices = np.array(dataset._indices)[keep_mask]

    # Rebuild clean dataset
    clean_windows = []
    for idx in keep_indices:
        clean_windows.append(data[idx:idx + window_size])
    if len(clean_windows) == 0:
        logger.warning("self-cleaning removed all windows, using original")
        return model

    clean_data = np.concatenate(clean_windows, axis=0)
    logger.info("self-cleaning round 2: %d/%d windows kept (removed %d)",
                len(clean_windows), len(errors), len(errors) - len(clean_windows))

    # Round 2
    return train_model(clean_data, n_sensors, hidden_dim, window_size,
                       device=device, **train_kwargs)
```

- [ ] **Step 5: Create src/training/export_onnx.py**

```python
import torch
from src.training.model import LSTMAutoencoder


def export_to_onnx(model: LSTMAutoencoder, path: str,
                   window_size: int, n_sensors: int) -> None:
    model.eval()
    dummy_input = torch.randn(1, window_size, n_sensors)
    torch.onnx.export(
        model, dummy_input, path,
        input_names=["input"],
        output_names=["reconstruction", "latent"],
        dynamic_axes={"input": {0: "batch"},
                      "reconstruction": {0: "batch"},
                      "latent": {0: "batch"}},
        opset_version=17,
    )
```

- [ ] **Step 6: Create src/detection/lstm_ae.py**

```python
import logging
import numpy as np
from collections.abc import Sequence
import onnxruntime as ort
from src.detection.base import Detector
from src.preprocessing.scaler import RobustScaler
from src.threshold.pot import POTThreshold
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent, Severity, DetectionSource

logger = logging.getLogger(__name__)


class LSTMAEDetector(Detector):
    def __init__(self, model_path: str, window_size: int = 128,
                 n_sensors: int = 1, sensor_names: list[str] | None = None):
        super().__init__("lstm_ae")
        self.session = ort.InferenceSession(model_path)
        self.window_size = window_size
        self.n_sensors = n_sensors
        self.sensor_names = sensor_names or []
        self.scaler = RobustScaler()
        self.thresholds: dict[str, POTThreshold] = {}
        self._buffer: list[dict] = []

    def configure(self, **kwargs) -> None:
        if "alpha" in kwargs:
            for t in self.thresholds.values():
                t.alpha = float(kwargs["alpha"])

    async def detect(self, data: SensorData,
                     history: Sequence[SensorData]) -> AnomalyEvent | None:
        relevant = [h for h in history if h.device_id == data.device_id]
        if len(relevant) < self.window_size:
            return None

        # Build input window from relevant sensors
        device_sensors = sorted(set(
            h.sensor_id for h in relevant[-self.window_size * 2:]
        ))
        if len(device_sensors) != self.n_sensors:
            return None

        window_data = self._build_window(relevant, device_sensors)
        if window_data is None:
            return None

        # Normalize
        input_tensor = window_data.astype(np.float32)[np.newaxis, :, :]
        ort_inputs = {self.session.get_inputs()[0].name: input_tensor}
        outputs = self.session.run(None, ort_inputs)
        recon = outputs[0][0]  # (window_size, n_sensors)

        # Per-sensor error
        errors = np.mean((window_data - recon) ** 2, axis=0)
        sensor_idx = device_sensors.index(data.sensor_id) if data.sensor_id in device_sensors else -1
        if sensor_idx < 0:
            return None

        error = float(errors[sensor_idx])

        # Initialize threshold per sensor if needed
        if data.sensor_id not in self.thresholds:
            self.thresholds[data.sensor_id] = POTThreshold(alpha=0.001, window=1000)
        self.thresholds[data.sensor_id].update(error)

        if not self.thresholds[data.sensor_id].is_anomaly(error):
            return None

        return AnomalyEvent(
            device_id=data.device_id,
            sensor_id=data.sensor_id,
            sensor_type=data.sensor_type.value,
            timestamp=data.timestamp,
            anomaly_score=min(error / max(self.thresholds[data.sensor_id].threshold, 1e-9), 1.0),
            severity=Severity.WARNING,
            detection_source=DetectionSource.LSTM_AE,
            evidence={"reconstruction_error": error,
                      "threshold": self.thresholds[data.sensor_id].threshold},
        )

    def _build_window(self, history, sensor_names):
        by_ts = {}
        for h in history:
            ts = h.timestamp
            if ts not in by_ts:
                by_ts[ts] = {}
            by_ts[ts][h.sensor_id] = h.value
        ts_sorted = sorted(by_ts.keys())[-self.window_size:]
        if len(ts_sorted) < self.window_size:
            return None
        rows = []
        for ts in ts_sorted:
            row = [by_ts[ts].get(s, 0.0) for s in sensor_names]
            rows.append(row)
        return np.array(rows, dtype=np.float32)
```

- [ ] **Step 7: Write model tests — tests/test_lstm_ae_model.py**

```python
import pytest
import torch
import numpy as np
from src.training.model import LSTMAutoencoder, reconstruction_error


class TestLSTMAutoencoder:
    @pytest.fixture
    def model(self):
        return LSTMAutoencoder(n_sensors=3, hidden_dim=32, window_size=64)

    def test_forward_shape(self, model):
        x = torch.randn(4, 64, 3)  # batch=4, window=64, sensors=3
        recon, latent = model(x)
        assert recon.shape == (4, 64, 3)
        assert latent.shape == (4, 32)

    def test_reconstruction_error_per_sensor(self):
        x = torch.ones(2, 10, 3)
        x_hat = x.clone()
        x_hat[:, :, 0] += 1.0  # error in sensor 0
        err = reconstruction_error(x, x_hat, per_sensor=True)
        assert err.shape == (2, 3)
        assert err[0, 0] > err[0, 1]

    def test_overfit_simple_signal(self, model):
        """Model should easily overfit a simple sine wave."""
        t = np.linspace(0, 4 * np.pi, 200)
        data = np.column_stack([
            np.sin(t),
            np.cos(t),
            np.sin(t + np.pi / 4),
        ]).astype(np.float32)

        from src.training.train import train_model
        trained = train_model(data, n_sensors=3, hidden_dim=16,
                             window_size=64, epochs=30, lr=0.01,
                             device="cpu")
        trained.eval()
        with torch.no_grad():
            x = torch.FloatTensor(data[:64]).unsqueeze(0)
            recon, _ = trained(x)
            loss = torch.nn.functional.mse_loss(recon, x)
            assert loss.item() < 0.1  # should fit simple sine well
```

- [ ] **Step 8: Run model tests**

```bash
python -m pytest tests/test_lstm_ae_model.py -v
```

Expected: 3 passed

- [ ] **Step 9: Commit**

```bash
git add src/training/ src/detection/lstm_ae.py tests/test_lstm_ae_model.py
git commit -m "feat: add LSTM-Autoencoder model and Phase 2 detector"
```

---

### Task 16: Concept Drift Monitor (Phase 3)

**Files:**
- Create: `src/drift/__init__.py`
- Create: `src/drift/monitor.py`

- [ ] **Step 1: Create src/drift/monitor.py**

```python
import math
import logging
from collections import deque
import numpy as np

logger = logging.getLogger(__name__)


class DriftMonitor:
    def __init__(self, window_size: int = 5000, threshold: float = 0.3):
        self.window_size = window_size
        self.threshold = threshold
        self._baseline: np.ndarray | None = None
        self._recent: deque[float] = deque(maxlen=window_size)

    def set_baseline(self, errors: list[float], n_bins: int = 50) -> None:
        if len(errors) < 100:
            return
        hist, _ = np.histogram(errors, bins=n_bins, density=True)
        self._baseline = hist + 1e-9
        logger.info("drift baseline set from %d errors", len(errors))

    def update(self, error: float) -> None:
        self._recent.append(error)

    def check_drift(self) -> float:
        if self._baseline is None or len(self._recent) < 100:
            return 0.0
        recent_hist, _ = np.histogram(list(self._recent), bins=len(self._baseline),
                                       density=True)
        recent_hist = recent_hist + 1e-9
        kl = float(np.sum(self._baseline * np.log(self._baseline / recent_hist)))
        if kl > self.threshold:
            logger.warning("drift detected: KL=%.4f > %.4f", kl, self.threshold)
        return kl
```

- [ ] **Step 2: Commit**

```bash
git add src/drift/
git commit -m "feat: add concept drift monitor"
```

---

### Task 17: Feedback Collector (Phase 3)

**Files:**
- Create: `src/feedback/__init__.py`
- Create: `src/feedback/collector.py`

- [ ] **Step 1: Create src/feedback/collector.py**

```python
import logging
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class FeedbackCollector:
    def __init__(self):
        self._feedback: list[dict] = []
        self._sensor_stats: dict[str, dict] = defaultdict(
            lambda: {"confirmed": 0, "rejected": 0, "total": 0}
        )

    def record(self, event_id: str, device_id: str, sensor_id: str,
               confirmed: bool, operator: str) -> None:
        self._feedback.append({
            "event_id": event_id, "device_id": device_id,
            "sensor_id": sensor_id, "confirmed": confirmed,
            "operator": operator, "recorded_at": datetime.now().isoformat(),
        })
        stats = self._sensor_stats[f"{device_id}:{sensor_id}"]
        stats["total"] += 1
        if confirmed:
            stats["confirmed"] += 1
        else:
            stats["rejected"] += 1

    def get_false_positive_rate(self, device_id: str, sensor_id: str) -> float:
        stats = self._sensor_stats.get(f"{device_id}:{sensor_id}")
        if stats is None or stats["total"] < 10:
            return 0.0
        return stats["rejected"] / stats["total"]

    def get_stats(self, device_id: str, sensor_id: str) -> dict:
        return dict(self._sensor_stats.get(f"{device_id}:{sensor_id}",
                    {"confirmed": 0, "rejected": 0, "total": 0}))
```

- [ ] **Step 2: Commit**

```bash
git add src/feedback/
git commit -m "feat: add feedback collector"
```

---

### Task 18: Final Integration and End-to-End Test

**Files:**
- Create: `tests/test_integration.py`

- [ ] **Step 1: Create tests/test_integration.py**

```python
import pytest
import asyncio
from datetime import datetime, timezone
from src.detection.engine import DetectionEngine
from src.detection.hard_boundary import HardBoundaryDetector
from src.detection.statistical import StatisticalDetector
from src.alerting.dedup import AlertDeduplicator
from src.alerting.router import AlertRouter
from src.alerting.channels import ConsoleChannel
from src.models.sensor import SensorData, SensorType
from tests.conftest import make_history


class TestEndToEnd:
    async def test_full_pipeline_normal(self):
        engine = DetectionEngine([
            HardBoundaryDetector(), StatisticalDetector(window_size=50)
        ])
        engine.detectors[0].configure("t1", hard_min=0, hard_max=100)

        router = AlertRouter()
        dedup = AlertDeduplicator(cooldown_seconds=300)
        router.dedup = dedup

        history = make_history(base_value=25.0, count=100, noise=0.3, sensor_id="t1")
        data = SensorData(
            device_id="d1", sensor_id="t1",
            sensor_type=SensorType.TEMPERATURE, value=25.5,
            timestamp=datetime.now(timezone.utc),
        )

        events = await engine.run(data, history)
        for event in events:
            await router.route(event)

        # Normal data should produce no alerts
        assert events == []

    async def test_full_pipeline_anomaly(self):
        engine = DetectionEngine([
            HardBoundaryDetector(), StatisticalDetector(window_size=50, sigma=3.0)
        ])
        engine.detectors[0].configure("t1", hard_min=0, hard_max=100)

        router = AlertRouter()

        history = make_history(base_value=25.0, count=100, noise=0.3, sensor_id="t1")
        anomaly = SensorData(
            device_id="d1", sensor_id="t1",
            sensor_type=SensorType.TEMPERATURE, value=80.0,
            timestamp=datetime.now(timezone.utc),
        )

        events = await engine.run(anomaly, history)
        assert len(events) >= 1

        for event in events:
            result = await router.route(event)
            assert result is True  # first alert should go through

    async def test_dedup_prevents_storm(self):
        engine = DetectionEngine([
            HardBoundaryDetector(), StatisticalDetector(window_size=50, sigma=3.0)
        ])
        engine.detectors[0].configure("t1", hard_min=0, hard_max=100)

        router = AlertRouter()
        history = make_history(base_value=25.0, count=100, noise=0.3, sensor_id="t1")

        # Send 5 anomalies in quick succession
        results = []
        for i in range(5):
            data = SensorData(
                device_id="d1", sensor_id="t1",
                sensor_type=SensorType.TEMPERATURE, value=80.0 + i,
                timestamp=datetime.now(timezone.utc),
            )
            events = await engine.run(data, history)
            for event in events:
                ok = await router.route(event)
                results.append(ok)

        # Only first should pass
        assert results[0] is True
        assert results[1] is False  # dedupped
```

- [ ] **Step 2: Run integration tests**

```bash
python -m pytest tests/test_integration.py -v
```

Expected: 3 passed

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration.py
git commit -m "test: add end-to-end integration tests"
```

---

## Implementation Order

1. Task 1: Project setup and dependencies
2. Task 2: Data models
3. Task 3: Detector base interface
4. Task 4: Hard boundary detector
5. Task 5: Statistical rules detector
6. Task 6: Detection engine
7. Task 7: Alert deduplication
8. Task 8: Alert channels and router
9. Task 9: POT dynamic threshold
10. Task 10: RobustScaler preprocessing
11. Task 11: Storage layer + Docker Compose
12. Task 12: MQTT ingestion
13. Task 13: FastAPI + WebSocket
14. Task 14: Main entrypoint
15. Task 15: LSTM-Autoencoder (Phase 2)
16. Task 16: Concept drift monitor (Phase 3)
17. Task 17: Feedback collector (Phase 3)
18. Task 18: End-to-end integration tests
