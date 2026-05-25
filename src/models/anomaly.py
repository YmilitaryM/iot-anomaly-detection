import uuid
from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field


class Severity(StrEnum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class DetectionSource(StrEnum):
    HARD_BOUNDARY = "hard_boundary"
    STATISTICAL = "statistical"
    LSTM_AE = "lstm_ae"


class AnomalyStatus(StrEnum):
    OPEN = "open"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


class AnomalyEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_id: str
    sensor_id: str
    sensor_type: str
    timestamp: datetime
    anomaly_score: float
    severity: Severity
    detection_source: DetectionSource
    evidence: dict = Field(default_factory=dict)
    status: AnomalyStatus = AnomalyStatus.OPEN
    confirmed_by: str | None = None
    confirmed_at: datetime | None = None
