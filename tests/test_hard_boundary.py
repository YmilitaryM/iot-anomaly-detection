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

    async def test_partial_config_does_not_clear_existing(self, detector, config):
        detector.configure("s1", **config)
        detector.configure("s1", hard_min=0)  # only one bound
        data = SensorData(device_id="d1", sensor_id="s1",
                          sensor_type=SensorType.TEMPERATURE, value=150.0,
                          timestamp=datetime.now())
        result = await detector.detect(data, [])
        assert result is not None  # bounds should still be active
