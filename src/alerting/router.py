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
