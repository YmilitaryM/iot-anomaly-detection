import numpy as np


class RobustScaler:
    """Median + IQR based scaler, resistant to outliers."""

    def __init__(self, with_centering: bool = True, with_scaling: bool = True):
        self.with_centering = with_centering
        self.with_scaling = with_scaling
        self._medians: dict[str, float] = {}
        self._iqrs: dict[str, float] = {}

    def fit(self, data: np.ndarray) -> "RobustScaler":
        q1, med, q3 = np.percentile(data, [25, 50, 75])
        self._medians["_default"] = med
        self._iqrs["_default"] = q3 - q1 if q3 > q1 else 1.0
        return self

    def transform(self, data: np.ndarray) -> np.ndarray:
        med = self._medians.get("_default", 0.0)
        iqr = self._iqrs.get("_default", 1.0)
        result = data.astype(np.float64).copy()
        if self.with_centering:
            result -= med
        if self.with_scaling and iqr > 1e-9:
            result /= iqr
        return result

    def inverse_transform(self, data: np.ndarray) -> np.ndarray:
        med = self._medians.get("_default", 0.0)
        iqr = self._iqrs.get("_default", 1.0)
        result = data.astype(np.float64).copy()
        if self.with_scaling and iqr > 1e-9:
            result *= iqr
        if self.with_centering:
            result += med
        return result

    def fit_multi(self, sensor_data: dict[str, np.ndarray]) -> "RobustScaler":
        for key, arr in sensor_data.items():
            q1, med, q3 = np.percentile(arr, [25, 50, 75])
            self._medians[key] = med
            self._iqrs[key] = q3 - q1 if q3 > q1 else 1.0
        return self

    def transform_multi(self, sensor_data: dict[str, np.ndarray]) -> dict[str, np.ndarray]:
        result = {}
        for key, arr in sensor_data.items():
            med = self._medians.get(key, 0.0)
            iqr = self._iqrs.get(key, 1.0)
            transformed = arr.astype(np.float64).copy()
            if self.with_centering:
                transformed -= med
            if self.with_scaling and iqr > 1e-9:
                transformed /= iqr
            result[key] = transformed
        return result
