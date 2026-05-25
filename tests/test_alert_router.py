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
