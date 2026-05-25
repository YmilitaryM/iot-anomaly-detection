import pytest
from datetime import datetime, timedelta
from src.models.sensor import SensorData, SensorType


def make_sensor_data(
    device_id: str = "dev-001",
    sensor_id: str = "temp-01",
    sensor_type: SensorType = SensorType.TEMPERATURE,
    value: float = 25.0,
    timestamp: datetime | None = None,
) -> SensorData:
    return SensorData(
        device_id=device_id,
        sensor_id=sensor_id,
        sensor_type=sensor_type,
        value=value,
        timestamp=timestamp or datetime.now(),
    )


def make_history(
    base_value: float,
    count: int,
    noise: float = 0.0,
    interval_seconds: float = 1.0,
    start_time: datetime | None = None,
    device_id: str = "dev-001",
    sensor_id: str = "temp-01",
) -> list[SensorData]:
    import random
    random.seed(42)
    t = start_time or datetime.now() - timedelta(seconds=count * interval_seconds)
    history = []
    for i in range(count):
        val = base_value + random.gauss(0, noise) if noise > 0 else base_value
        history.append(SensorData(
            device_id=device_id,
            sensor_id=sensor_id,
            sensor_type=SensorType.TEMPERATURE,
            value=val,
            timestamp=t + timedelta(seconds=i * interval_seconds),
        ))
    return history
