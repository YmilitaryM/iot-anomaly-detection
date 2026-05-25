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
