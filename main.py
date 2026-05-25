import asyncio
import logging
from src.config import settings
from src.api.app import app
from src.api.deps import set_engine, set_alert_router
from src.ingestion.mqtt import MQTTIngestor
from src.detection.engine import DetectionEngine
from src.detection.hard_boundary import HardBoundaryDetector
from src.detection.statistical import StatisticalDetector
from src.alerting.router import AlertRouter
from src.alerting.channels import ConsoleChannel
from src.models.sensor import SensorData
from src.models.anomaly import AnomalyEvent
from src.storage.timescaledb import TimescaleSession, insert_sensor_data
from src.api.routes.alerts import store_alert
from src.api.websocket import broadcaster

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)


async def handle_sensor_data(data: SensorData) -> None:
    from src.api.deps import get_engine, get_alert_router
    engine = get_engine()
    events: list[AnomalyEvent] = await engine.run(data)

    async with TimescaleSession() as session:
        await insert_sensor_data(session, data)

    router = get_alert_router()
    for event in events:
        event_dict = event.model_dump()
        store_alert(event_dict)
        await router.route(event)
        await broadcaster.broadcast(event_dict)


def main():
    # Init detectors — creates engine with default detectors
    from src.api.deps import get_engine, get_alert_router
    engine = get_engine()
    router = get_alert_router()
    from src.models.anomaly import Severity
    router.add_channel(Severity.CRITICAL, ConsoleChannel())
    router.add_channel(Severity.WARNING, ConsoleChannel())

    ingestor = MQTTIngestor(handler=handle_sensor_data)

    import uvicorn
    import threading

    def run_api():
        uvicorn.run(app, host=settings.api_host, port=settings.api_port)

    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()
    logger.info("API server starting on %s:%s", settings.api_host, settings.api_port)

    asyncio.run(ingestor.start())


if __name__ == "__main__":
    main()
