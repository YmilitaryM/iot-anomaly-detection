from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field


class SensorType(StrEnum):
    TEMPERATURE = "temperature"
    VIBRATION = "vibration"
    PRESSURE = "pressure"
    CURRENT = "current"
    POWER = "power"
    HUMIDITY = "humidity"
    DISCRETE = "discrete"


class SensorData(BaseModel):
    device_id: str
    sensor_id: str
    sensor_type: SensorType
    value: float
    timestamp: datetime
    unit: str | None = None


class SensorConfig(BaseModel):
    sensor_id: str
    sensor_type: SensorType
    unit: str | None = None
    hard_min: float | None = None
    hard_max: float | None = None
    expected_interval_seconds: float = 1.0
