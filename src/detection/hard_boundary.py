import logging
from collections.abc import Sequence
from src.detection.base import Detector
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent, Severity, DetectionSource

logger = logging.getLogger(__name__)


class HardBoundaryDetector(Detector):
    def __init__(self):
        super().__init__("hard_boundary")
        self._bounds: dict[str, tuple[float, float]] = {}

    def configure(self, sensor_id: str, hard_min: float | None = None,
                  hard_max: float | None = None, **kwargs) -> None:
        if hard_min is not None and hard_max is not None:
            self._bounds[sensor_id] = (hard_min, hard_max)
            logger.info("configured %s: [%s, %s]", sensor_id, hard_min, hard_max)
        elif hard_min is None and hard_max is None:
            if sensor_id in self._bounds:
                del self._bounds[sensor_id]
                logger.info("cleared config for %s", sensor_id)

    async def detect(self, data: SensorData,
                     history: Sequence[SensorData]) -> AnomalyEvent | None:
        bounds = self._bounds.get(data.sensor_id)
        if bounds is None:
            return None
        lo, hi = bounds
        if lo <= data.value <= hi:
            return None
        return AnomalyEvent(
            device_id=data.device_id,
            sensor_id=data.sensor_id,
            sensor_type=data.sensor_type.value,
            timestamp=data.timestamp,
            anomaly_score=1.0,
            severity=Severity.CRITICAL,
            detection_source=DetectionSource.HARD_BOUNDARY,
            evidence={"value": data.value, "min": lo, "max": hi},
        )
