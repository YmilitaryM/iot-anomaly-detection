from fastapi import APIRouter, Query
from src.api.deps import get_engine

router = APIRouter(prefix="/api/devices", tags=["devices"])

# In-memory registry populated via config and auto-registered during ingest
_devices: dict[str, dict] = {}


def register_device(device_id: str, device_type: str = "unknown") -> None:
    if device_id not in _devices:
        _devices[device_id] = {
            "device_id": device_id,
            "device_type": device_type,
            "training_status": "none",
            "model_version": "",
        }


@router.get("")
async def list_devices():
    # Also query TimescaleDB for devices that have data but weren't configured
    from src.storage.timescaledb import timescale_engine
    from sqlalchemy import text
    async with timescale_engine.begin() as conn:
        result = await conn.execute(text(
            "SELECT DISTINCT device_id, sensor_type FROM sensor_data"
        ))
        for row in result.fetchall():
            register_device(row[0], row[1] or "unknown")
    return {"total": len(_devices), "items": list(_devices.values())}


@router.post("/{device_id}/sensors/{sensor_id}/config")
async def configure_sensor(device_id: str, sensor_id: str,
                           hard_min: float | None = None,
                           hard_max: float | None = None):
    engine = get_engine()
    for detector in engine.detectors:
        if detector.name == "hard_boundary":
            detector.configure(sensor_id, hard_min=hard_min, hard_max=hard_max)
            return {"ok": True, "device_id": device_id, "sensor_id": sensor_id}
    return {"ok": False, "error": "hard_boundary detector not found"}
