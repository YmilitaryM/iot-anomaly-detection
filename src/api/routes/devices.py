from fastapi import APIRouter
from src.api.deps import get_engine

router = APIRouter(prefix="/api/devices", tags=["devices"])

_devices: dict[str, dict] = {}


@router.get("")
async def list_devices():
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
