import pytest
import random
from src.threshold.pot import POTThreshold


class TestPOTThreshold:
    @pytest.fixture
    def pot(self):
        return POTThreshold(alpha=0.01, window=500)

    def test_initial_threshold_is_infinite(self, pot):
        assert pot.threshold == float("inf")

    def test_fit_sets_threshold(self, pot):
        random.seed(42)
        data = [random.gauss(0, 1) for _ in range(600)]
        pot.update_batch(data)
        assert pot.threshold > 0
        assert pot.threshold < float("inf")

    def test_threshold_adapts_to_larger_values(self, pot):
        random.seed(42)
        normal = [abs(random.gauss(0, 1)) for _ in range(500)]
        pot.update_batch(normal)
        t1 = pot.threshold
        large = [abs(random.gauss(5, 1)) for _ in range(1000)]
        pot.update_batch(large)
        t2 = pot.threshold
        assert t2 > t1

    def test_is_anomaly(self, pot):
        random.seed(42)
        data = [abs(random.gauss(0, 1)) for _ in range(600)]
        pot.update_batch(data)
        assert not pot.is_anomaly(0.5)
        assert pot.is_anomaly(pot.threshold * 3)

    def test_shorter_than_initial_data(self, pot):
        data = [1.0, 2.0, 3.0]
        pot.update_batch(data)
        assert pot.threshold == float("inf")
