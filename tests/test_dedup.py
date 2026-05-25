import pytest
from datetime import datetime, timedelta
from src.alerting.dedup import AlertDeduplicator
from src.models.anomaly import AnomalyEvent, Severity, DetectionSource


class TestAlertDeduplicator:
    @pytest.fixture
    def dedup(self):
        return AlertDeduplicator(cooldown_seconds=300)

    def make_event(self, device_id="d1", sensor_id="s1",
                   timestamp=None, score=0.9, severity=Severity.WARNING):
        return AnomalyEvent(
            device_id=device_id, sensor_id=sensor_id,
            sensor_type="temperature",
            timestamp=timestamp or datetime.now(),
            anomaly_score=score, severity=severity,
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
