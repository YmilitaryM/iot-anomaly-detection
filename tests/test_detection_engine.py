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
        history = make_history(base_value=25.0, count=100, noise=0.3, sensor_id="t1")
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
        history = make_history(base_value=25.0, count=100, noise=0.3, sensor_id="t1")
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=200.0,
                          timestamp=datetime.now())
        results = await engine.run(data, history)
        assert len(results) == 2

    async def test_no_detectors_configured(self):
        engine = DetectionEngine(detectors=[])
        data = SensorData(device_id="d1", sensor_id="t1",
                          sensor_type=SensorType.TEMPERATURE, value=25.0,
                          timestamp=datetime.now())
        results = await engine.run(data, [])
        assert results == []
