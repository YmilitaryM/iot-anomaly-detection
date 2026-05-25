import logging
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from src.config import settings

logger = logging.getLogger(__name__)

timescale_engine = create_async_engine(settings.timescale_dsn, echo=False)
TimescaleSession = async_sessionmaker(timescale_engine, expire_on_commit=False)


async def init_timescaledb() -> None:
    async with timescale_engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS timescaledb"))
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS sensor_data (
                time TIMESTAMPTZ NOT NULL,
                device_id TEXT NOT NULL,
                sensor_id TEXT NOT NULL,
                sensor_type TEXT NOT NULL,
                value DOUBLE PRECISION NOT NULL,
                unit TEXT
            )
        """))
        await conn.execute(text("""
            SELECT create_hypertable('sensor_data', 'time', if_not_exists => TRUE);
        """))
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_sensor_data_device_sensor
            ON sensor_data (device_id, sensor_id, time DESC);
        """))


async def insert_sensor_data(session: AsyncSession, data) -> None:
    await session.execute(text("""
        INSERT INTO sensor_data (time, device_id, sensor_id, sensor_type, value, unit)
        VALUES (:time, :device_id, :sensor_id, :sensor_type, :value, :unit)
    """), {
        "time": data.timestamp,
        "device_id": data.device_id,
        "sensor_id": data.sensor_id,
        "sensor_type": data.sensor_type.value,
        "value": data.value,
        "unit": data.unit,
    })
    await session.commit()


async def query_sensor_history(
    device_id: str, sensor_id: str,
    start: datetime, end: datetime,
    limit: int = 10000,
) -> list[dict]:
    async with TimescaleSession() as session:
        result = await session.execute(text("""
            SELECT time, device_id, sensor_id, sensor_type, value, unit
            FROM sensor_data
            WHERE device_id = :device_id AND sensor_id = :sensor_id
              AND time >= :start AND time <= :end
            ORDER BY time DESC
            LIMIT :limit
        """), {"device_id": device_id, "sensor_id": sensor_id,
               "start": start, "end": end, "limit": limit})
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]
