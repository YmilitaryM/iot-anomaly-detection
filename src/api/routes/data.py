from fastapi import APIRouter, Query, HTTPException

router = APIRouter(prefix="/api/data", tags=["data"])


@router.get("/sensors/{device_id}/{sensor_id}")
async def query_sensor_data(
    device_id: str,
    sensor_id: str,
    start: str,
    end: str,
    limit: int = Query(1000, le=10000),
):
    from datetime import datetime
    from src.storage.timescaledb import query_sensor_history
    try:
        s = datetime.fromisoformat(start)
        e = datetime.fromisoformat(end)
    except ValueError:
        raise HTTPException(400, "invalid ISO datetime for start/end")
    rows = await query_sensor_history(device_id, sensor_id, s, e, limit)
    return {"device_id": device_id, "sensor_id": sensor_id, "count": len(rows),
            "data": rows}
