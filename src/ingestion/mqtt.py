import json
import logging
from datetime import datetime
from collections.abc import Callable, Awaitable
import aiomqtt
from src.config import settings
from src.models.sensor import SensorData, SensorType

logger = logging.getLogger(__name__)

Handler = Callable[[SensorData], Awaitable[None]]


class MQTTIngestor:
    def __init__(self, handler: Handler):
        self.handler = handler
        self._client: aiomqtt.Client | None = None

    async def start(self) -> None:
        while True:
            try:
                async with aiomqtt.Client(hostname=settings.mqtt_host,
                                          port=settings.mqtt_port) as client:
                    self._client = client
                    await client.subscribe(settings.mqtt_topic)
                    logger.info("MQTT connected, subscribed to %s", settings.mqtt_topic)
                    async for message in client.messages:
                        await self._handle_message(message)
            except aiomqtt.MqttError:
                logger.exception("MQTT connection lost, reconnecting in 5s...")
                import asyncio
                await asyncio.sleep(5)

    async def stop(self) -> None:
        if self._client:
            await self._client.__aexit__(None, None, None)

    async def _handle_message(self, message) -> None:
        try:
            payload = json.loads(message.payload)
            data = SensorData(
                device_id=payload["device_id"],
                sensor_id=payload["sensor_id"],
                sensor_type=SensorType(payload["sensor_type"]),
                value=float(payload["value"]),
                timestamp=datetime.fromisoformat(payload["timestamp"]),
                unit=payload.get("unit"),
            )
            await self.handler(data)
        except (json.JSONDecodeError, KeyError, ValueError):
            logger.warning("invalid MQTT message on %s: %s",
                           message.topic, message.payload[:200])
