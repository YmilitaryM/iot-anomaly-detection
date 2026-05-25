from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import alerts, data, devices
from src.api.websocket import broadcaster
from src.api.deps import get_engine, get_alert_router
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent
from src.storage.timescaledb import TimescaleSession, insert_sensor_data
from src.api.routes.alerts import store_alert
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.storage.postgres import init_db
    from src.storage.timescaledb import init_timescaledb
    await init_db()
    await init_timescaledb()
    logger.info("database initialized")
    yield


app = FastAPI(title="IoT Anomaly Detection", version="0.1.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"],
                   allow_headers=["*"])

app.include_router(alerts.router)
app.include_router(data.router)
app.include_router(devices.router)


@app.websocket("/ws/alerts")
async def ws_alerts(websocket: WebSocket):
    await broadcaster.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        broadcaster.disconnect(websocket)


@app.post("/api/ingest")
async def ingest(data: SensorData):
    engine = get_engine()
    events: list[AnomalyEvent] = await engine.run(data)

    # Store to TimescaleDB
    async with TimescaleSession() as session:
        await insert_sensor_data(session, data)

    router = get_alert_router()
    for event in events:
        event_dict = event.model_dump()
        store_alert(event_dict)
        await router.route(event)
        await broadcaster.broadcast(event_dict)

    return {"received": True, "anomalies": len(events)}
