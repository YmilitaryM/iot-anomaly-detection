import pytest
from datetime import datetime, timezone
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient, ASGITransport
from src.api.app import app
from src.api.deps import set_engine, set_alert_router
from src.detection.engine import DetectionEngine
from src.detection.hard_boundary import HardBoundaryDetector
from src.alerting.router import AlertRouter


@pytest.fixture
def client():
    hb = HardBoundaryDetector()
    hb.configure("t1", hard_min=0, hard_max=100)
    engine = DetectionEngine(detectors=[hb])
    set_engine(engine)
    router = AlertRouter()
    set_alert_router(router)
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture(autouse=True)
def mock_timescaledb():
    """Prevent ingest endpoint from connecting to a real database."""
    mock_session = AsyncMock()
    mock_session.__aenter__.return_value = mock_session
    with patch("src.api.app.TimescaleSession", return_value=mock_session):
        with patch("src.api.app.insert_sensor_data", AsyncMock()):
            yield


@pytest.mark.asyncio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        resp = await c.get("/docs")
        assert resp.status_code == 200


@pytest.mark.asyncio
async def test_ingest_normal_data(client):
    payload = {
        "device_id": "d1", "sensor_id": "t1",
        "sensor_type": "temperature", "value": 50.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "unit": "C"
    }
    resp = await client.post("/api/ingest", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["received"] is True
    assert data["anomalies"] == 0


@pytest.mark.asyncio
async def test_ingest_anomaly_triggers_alert(client):
    payload = {
        "device_id": "d1", "sensor_id": "t1",
        "sensor_type": "temperature", "value": 150.0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "unit": "C"
    }
    resp = await client.post("/api/ingest", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["anomalies"] >= 1


@pytest.mark.asyncio
async def test_alerts_endpoint(client):
    resp = await client.get("/api/alerts")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data
