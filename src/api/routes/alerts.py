from fastapi import APIRouter, Depends, HTTPException, Query
from src.api.deps import get_engine

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

# In-memory store for demo; replaced by PostgreSQL in production
_alerts_store: list[dict] = []


@router.get("")
async def list_alerts(limit: int = Query(50, le=500), offset: int = 0):
    return {
        "total": len(_alerts_store),
        "items": _alerts_store[offset:offset + limit],
    }


@router.post("/{event_id}/feedback")
async def submit_feedback(event_id: str, confirmed: bool, operator: str = "anonymous"):
    for alert in _alerts_store:
        if alert["event_id"] == event_id:
            alert["status"] = "confirmed" if confirmed else "rejected"
            alert["confirmed_by"] = operator
            alert["confirmed_at"] = __import__("datetime").datetime.now().isoformat()
            return {"ok": True, "event_id": event_id}
    raise HTTPException(404, "alert not found")


def store_alert(event_dict: dict) -> None:
    _alerts_store.insert(0, event_dict)
    if len(_alerts_store) > 10000:
        _alerts_store.pop()
