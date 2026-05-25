import math
import logging
from collections import deque

logger = logging.getLogger(__name__)


class POTThreshold:
    """Peak-Over-Threshold: fits GPD to tail of error distribution."""

    def __init__(self, alpha: float = 0.001, window: int = 1000,
                 initial_quantile: float = 0.98):
        self.alpha = alpha
        self.window = window
        self.initial_quantile = initial_quantile
        self._buffer: deque[float] = deque(maxlen=window)
        self._threshold: float = float("inf")
        self._params: tuple[float, float] | None = None

    @property
    def threshold(self) -> float:
        return self._threshold

    def update(self, value: float) -> None:
        self._buffer.append(value)
        if len(self._buffer) >= self.window // 2:
            self._refit()

    def update_batch(self, values: list[float]) -> None:
        for v in values:
            self._buffer.append(v)
        if len(self._buffer) >= self.window // 2:
            self._refit()

    def is_anomaly(self, value: float) -> bool:
        return value > self._threshold

    def _refit(self) -> None:
        data = sorted(self._buffer)
        n = len(data)
        if n < 100:
            return
        # Use upper quantile as threshold for GPD fit
        t_index = int(n * self.initial_quantile)
        t = data[t_index]
        excesses = [x - t for x in data if x > t]
        if len(excesses) < 10:
            # Fallback: use empirical quantile
            self._threshold = data[int(n * (1 - self.alpha))]
            return
        # Fit GPD via MLE (approximation via method of moments)
        excess_mean = sum(excesses) / len(excesses)
        excess_var = sum((x - excess_mean) ** 2 for x in excesses) / len(excesses)
        if excess_var < 1e-9 or excess_mean < 1e-9:
            self._threshold = data[int(n * (1 - self.alpha))]
            return
        shape = 0.5 * (1 - (excess_mean ** 2 / excess_var))
        scale = 0.5 * excess_mean * ((excess_mean ** 2 / excess_var) + 1)

        # GPD quantile: z_q = t + (scale/xi) * (( (n/Nt * alpha)^(-xi) ) - 1)
        Nt = len(excesses)
        try:
            z_q = t + (scale / shape) * (((n / Nt) * self.alpha) ** (-shape) - 1)
            if z_q > t and not math.isnan(z_q) and not math.isinf(z_q):
                self._threshold = z_q
                self._params = (shape, scale)
            else:
                self._threshold = data[int(n * (1 - self.alpha))]
        except (OverflowError, ValueError, ZeroDivisionError):
            self._threshold = data[int(n * (1 - self.alpha))]
