import logging
from collections import deque
import numpy as np

logger = logging.getLogger(__name__)


class DriftMonitor:
    def __init__(self, window_size: int = 5000, threshold: float = 0.3):
        self.window_size = window_size
        self.threshold = threshold
        self._baseline: np.ndarray | None = None
        self._recent: deque[float] = deque(maxlen=window_size)

    def set_baseline(self, errors: list[float], n_bins: int = 50) -> None:
        if len(errors) < 100:
            return
        hist, _ = np.histogram(errors, bins=n_bins, density=True)
        self._baseline = hist + 1e-9
        logger.info("drift baseline set from %d errors", len(errors))

    def update(self, error: float) -> None:
        self._recent.append(error)

    def check_drift(self) -> float:
        if self._baseline is None or len(self._recent) < 100:
            return 0.0
        recent_hist, _ = np.histogram(list(self._recent), bins=len(self._baseline),
                                       density=True)
        recent_hist = recent_hist + 1e-9
        kl = float(np.sum(self._baseline * np.log(self._baseline / recent_hist)))
        if kl > self.threshold:
            logger.warning("drift detected: KL=%.4f > %.4f", kl, self.threshold)
        return kl
