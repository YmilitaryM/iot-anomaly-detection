import logging
import numpy as np
from collections.abc import Sequence
import onnxruntime as ort
from src.detection.base import Detector
from src.threshold.pot import POTThreshold
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent, Severity, DetectionSource

logger = logging.getLogger(__name__)


class LSTMAEDetector(Detector):
    def __init__(self, model_path: str, window_size: int = 128,
                 n_sensors: int = 1, sensor_names: list[str] | None = None):
        super().__init__("lstm_ae")
        self.session = ort.InferenceSession(model_path)
        self.window_size = window_size
        self.n_sensors = n_sensors
        self.sensor_names = sensor_names or []
        self.thresholds: dict[str, POTThreshold] = {}

    def configure(self, **kwargs) -> None:
        if "alpha" in kwargs:
            for t in self.thresholds.values():
                t.alpha = float(kwargs["alpha"])

    async def detect(self, data: SensorData,
                     history: Sequence[SensorData]) -> AnomalyEvent | None:
        relevant = [h for h in history if h.device_id == data.device_id]
        if len(relevant) < self.window_size:
            return None

        # Build input window from relevant sensors
        device_sensors = sorted(set(
            h.sensor_id for h in relevant[-self.window_size * 2:]
        ))
        if len(device_sensors) != self.n_sensors:
            return None

        window_data = self._build_window(relevant, device_sensors)
        if window_data is None:
            return None

        # Normalize
        input_tensor = window_data.astype(np.float32)[np.newaxis, :, :]
        ort_inputs = {self.session.get_inputs()[0].name: input_tensor}
        outputs = self.session.run(None, ort_inputs)
        recon = outputs[0][0]  # (window_size, n_sensors)

        # Per-sensor error
        errors = np.mean((window_data - recon) ** 2, axis=0)
        sensor_idx = device_sensors.index(data.sensor_id) if data.sensor_id in device_sensors else -1
        if sensor_idx < 0:
            return None

        error = float(errors[sensor_idx])

        # Initialize threshold per sensor if needed
        if data.sensor_id not in self.thresholds:
            self.thresholds[data.sensor_id] = POTThreshold(alpha=0.001, window=1000)
        self.thresholds[data.sensor_id].update(error)

        if not self.thresholds[data.sensor_id].is_anomaly(error):
            return None

        return AnomalyEvent(
            device_id=data.device_id,
            sensor_id=data.sensor_id,
            sensor_type=data.sensor_type,
            timestamp=data.timestamp,
            anomaly_score=min(error / max(self.thresholds[data.sensor_id].threshold, 1e-9), 1.0),
            severity=Severity.WARNING,
            detection_source=DetectionSource.LSTM_AE,
            evidence={"reconstruction_error": error,
                      "threshold": self.thresholds[data.sensor_id].threshold},
        )

    def _build_window(self, history, sensor_names):
        by_ts = {}
        for h in history:
            ts = h.timestamp
            if ts not in by_ts:
                by_ts[ts] = {}
            by_ts[ts][h.sensor_id] = h.value
        ts_sorted = sorted(by_ts.keys())[-self.window_size:]
        if len(ts_sorted) < self.window_size:
            return None
        rows = []
        for ts in ts_sorted:
            row = [by_ts[ts].get(s, 0.0) for s in sensor_names]
            rows.append(row)
        return np.array(rows, dtype=np.float32)
