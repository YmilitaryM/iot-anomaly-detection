import pytest
import numpy as np
from src.preprocessing.scaler import RobustScaler


class TestRobustScaler:
    @pytest.fixture
    def scaler(self):
        return RobustScaler()

    def test_fit_transform_centers_on_median(self, scaler):
        data = np.array([1.0, 2.0, 3.0, 4.0, 100.0])  # outlier at end
        scaler.fit(data)
        transformed = scaler.transform(data)
        assert abs(np.median(transformed)) < 1.0

    def test_outlier_resistant(self, scaler):
        data = np.array([10.0, 11.0, 9.0, 10.5, 10.2, 500.0])
        scaler.fit(data)
        transformed = scaler.transform(data)
        # The 500.0 should still be large but not dominate normalization
        assert transformed[-1] > 3.0

    def test_fit_multiple_sensors(self, scaler):
        sensor_data = {
            "temp": np.array([20.0, 21.0, 19.0, 22.0, 20.5]),
            "vib": np.array([0.1, 0.12, 0.09, 0.11, 0.1]),
        }
        scaler.fit_multi(sensor_data)
        result = scaler.transform_multi(sensor_data)
        for key in sensor_data:
            assert result[key].shape == sensor_data[key].shape
            assert abs(np.median(result[key])) < 0.5

    def test_inverse_transform(self, scaler):
        data = np.array([10.0, 20.0, 30.0])
        scaler.fit(data)
        transformed = scaler.transform(data)
        restored = scaler.inverse_transform(transformed)
        np.testing.assert_array_almost_equal(restored, data)
