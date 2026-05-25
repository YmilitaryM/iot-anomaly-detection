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
