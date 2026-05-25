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
