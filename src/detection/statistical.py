import math
import logging
from collections.abc import Sequence
from src.detection.base import Detector
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent, Severity, DetectionSource

logger = logging.getLogger(__name__)


class StatisticalDetector(Detector):
    def __init__(self, window_size: int = 100, sigma: float = 3.0,
                 max_rate_of_change: float | None = None):
        super().__init__("statistical")
        self.window_size = window_size
        self.sigma = sigma
        self.max_rate_of_change = max_rate_of_change

    def configure(self, **kwargs) -> None:
        if "window_size" in kwargs:
            self.window_size = int(kwargs["window_size"])
        if "sigma" in kwargs:
            self.sigma = float(kwargs["sigma"])
        if "max_rate_of_change" in kwargs:
            self.max_rate_of_change = float(kwargs["max_rate_of_change"])

    async def detect(self, data: SensorData,
                     history: Sequence[SensorData]) -> AnomalyEvent | None:
        relevant = [h for h in history if h.sensor_id == data.sensor_id]
        if len(relevant) < self.window_size // 2:
            return None

        window = relevant[-self.window_size:]
        values = [h.value for h in window]
        n = len(values)
        mean = sum(values) / n
        variance = sum((v - mean) ** 2 for v in values) / n
        std = math.sqrt(variance) if variance > 0 else 1e-9

        z_score = abs(data.value - mean) / std
        sigma_score = min(z_score / self.sigma, 1.0)

        # Rate-of-change check
        roc_violation = False
        if self.max_rate_of_change is not None and len(relevant) >= 2:
            prev = relevant[-1]
            dt = (data.timestamp - prev.timestamp).total_seconds()
            if dt > 0:
                roc = abs(data.value - prev.value) / dt
                if roc > self.max_rate_of_change:
                    roc_violation = True

        if z_score < self.sigma and not roc_violation:
            return None

        severity = Severity.WARNING
        if z_score > self.sigma * 2:
            severity = Severity.CRITICAL

        return AnomalyEvent(
            device_id=data.device_id,
            sensor_id=data.sensor_id,
            sensor_type=data.sensor_type.value,
            timestamp=data.timestamp,
            anomaly_score=round(sigma_score, 4),
            severity=severity,
            detection_source=DetectionSource.STATISTICAL,
            evidence={
                "value": data.value,
                "mean": round(mean, 4),
                "std": round(std, 4),
                "z_score": round(z_score, 4),
                "sigma": self.sigma,
                "window_size": n,
                "roc_violation": roc_violation,
            },
        )
