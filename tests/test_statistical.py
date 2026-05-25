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
        history = make_history(base_value=25.0, count=100, noise=0.5, sensor_id="t1")
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=25.3,
                          timestamp=datetime.now())
        result = await detector.detect(data, history)
        assert result is None

    async def test_spike_triggers_alert(self, detector):
        history = make_history(base_value=25.0, count=100, noise=0.3, sensor_id="t1")
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=50.0,
                          timestamp=datetime.now())
        result = await detector.detect(data, history)
        assert result is not None
        assert result.detection_source == DetectionSource.STATISTICAL
        assert result.anomaly_score > 0.5

    async def test_insufficient_history_returns_none(self, detector):
        history = make_history(base_value=25.0, count=5, noise=0.5, sensor_id="t1")
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=50.0,
                          timestamp=datetime.now())
        result = await detector.detect(data, history)
        assert result is None

    async def test_rate_of_change_detection(self, detector):
        now = datetime.now()
        history = make_history(base_value=25.0, count=50, noise=0.1, sensor_id="t1",
                               start_time=now - timedelta(seconds=55))
        history.extend([
            SensorData(device_id="d1", sensor_id="t1",
                       sensor_type=SensorType.TEMPERATURE, value=25.0,
                       timestamp=now - timedelta(seconds=2)),
            SensorData(device_id="d1", sensor_id="t1",
                       sensor_type=SensorType.TEMPERATURE, value=25.1,
                       timestamp=now - timedelta(seconds=1)),
        ])
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=80.0,
                          timestamp=now)
        result = await detector.detect(data, history)
        assert result is not None

    async def test_edge_case_near_boundary(self, detector):
        history = make_history(base_value=25.0, count=100, noise=0.5, sensor_id="t1")
        mean = sum(h.value for h in history) / len(history)
        std = math.sqrt(sum((h.value - mean)**2 for h in history) / len(history))
        near_3sigma = mean + 2.9 * std
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=near_3sigma,
                          timestamp=datetime.now())
        result = await detector.detect(data, history)
        assert result is None
