from abc import ABC, abstractmethod
from collections.abc import Sequence
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent


class Detector(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def detect(self, data: SensorData, history: Sequence[SensorData]) -> AnomalyEvent | None:
        """Return AnomalyEvent if anomaly detected, None otherwise."""
        ...

    @abstractmethod
    def configure(self, **kwargs) -> None:
        """Update detector parameters at runtime."""
        ...
