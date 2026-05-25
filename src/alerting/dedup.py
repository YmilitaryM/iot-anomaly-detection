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
        elapsed = event.timestamp.timestamp() - self._last_alert[key]
        return elapsed < self.cooldown

    def record(self, event: AnomalyEvent) -> None:
        key = self._key(event)
        self._last_alert[key] = event.timestamp.timestamp()
        self._last_severity[key] = event.severity
        logger.debug("recorded alert for %s at severity=%s", key, event.severity)

    @staticmethod
    def _severity_rank(sev: Severity) -> int:
        return {Severity.INFO: 0, Severity.WARNING: 1, Severity.CRITICAL: 2}[sev]
