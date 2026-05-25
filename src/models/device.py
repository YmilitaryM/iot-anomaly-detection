from enum import StrEnum
from pydantic import BaseModel, Field


class TrainingStatus(StrEnum):
    ACCUMULATING = "accumulating"
    TRAINING = "training"
    ACTIVE = "active"
    DEGRADED = "degraded"


class DeviceMetadata(BaseModel):
    device_id: str
    device_type: str
    display_name: str = ""
    sensor_configs: list = Field(default_factory=list)
    training_status: TrainingStatus = TrainingStatus.ACCUMULATING
    model_version: str = ""
