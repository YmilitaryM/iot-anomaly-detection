from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {"env_prefix": "IOT_", "env_nested_delimiter": "__"}

    # MQTT
    mqtt_host: str = "localhost"
    mqtt_port: int = 1883
    mqtt_topic: str = "sensors/#"

    # PostgreSQL
    postgres_dsn: str = "postgresql+asyncpg://iot:iot@localhost:5432/iot"

    # TimescaleDB (same PG instance, different schema handling)
    timescale_dsn: str = "postgresql+asyncpg://iot:iot@localhost:5432/iot"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Detection
    dedup_window_seconds: int = 300
    hard_boundary_enabled: bool = True
    statistical_enabled: bool = True
    lstm_ae_enabled: bool = False
    statistical_window_size: int = 100
    statistical_sigma: float = 3.0

    # Model
    model_dir: Path = Path("models")
    model_window_size: int = 128
    model_hidden_dim: int = 64
    training_min_samples: int = 65_000

    # POT
    pot_alpha: float = 0.001
    pot_window: int = 1000

    # Alerting
    dingtalk_webhook: str = ""
    feishu_webhook: str = ""
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    alert_from_email: str = ""

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000


settings = Settings()
