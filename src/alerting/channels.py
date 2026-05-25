import logging
from abc import ABC, abstractmethod
from src.models.anomaly import AnomalyEvent

logger = logging.getLogger(__name__)


class AlertChannel(ABC):
    @abstractmethod
    async def send(self, event: AnomalyEvent) -> bool:
        ...


class ConsoleChannel(AlertChannel):
    async def send(self, event: AnomalyEvent) -> bool:
        logger.warning(
            "[%s] %s/%s: %s (score=%.3f)",
            event.severity.value.upper(),
            event.device_id, event.sensor_id,
            event.detection_source.value, event.anomaly_score,
        )
        return True


class DingTalkChannel(AlertChannel):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, event: AnomalyEvent) -> bool:
        import httpx
        if not self.webhook_url:
            return False
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "msgtype": "text",
                    "text": {
                        "content": (
                            f"[{event.severity.value.upper()}] IoT Alert\n"
                            f"Device: {event.device_id}\n"
                            f"Sensor: {event.sensor_id} ({event.sensor_type})\n"
                            f"Score: {event.anomaly_score:.3f}\n"
                            f"Source: {event.detection_source.value}\n"
                            f"Time: {event.timestamp.isoformat()}"
                        )
                    }
                }
                r = await client.post(self.webhook_url, json=payload, timeout=5)
                return r.is_success
        except Exception:
            logger.exception("DingTalk send failed")
            return False


class FeishuChannel(AlertChannel):
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send(self, event: AnomalyEvent) -> bool:
        import httpx
        if not self.webhook_url:
            return False
        try:
            async with httpx.AsyncClient() as client:
                payload = {
                    "msg_type": "interactive",
                    "card": {
                        "header": {
                            "title": {"tag": "plain_text",
                                      "content": f"IoT Alert - {event.severity.value.upper()}"},
                            "template": "red" if event.severity.value == "critical" else "yellow",
                        },
                        "elements": [
                            {"tag": "div", "text": {"tag": "lark_md",
                                     "content": f"**Device:** {event.device_id}\n"
                                                f"**Sensor:** {event.sensor_id}\n"
                                                f"**Score:** {event.anomaly_score:.3f}\n"
                                                f"**Time:** {event.timestamp.isoformat()}"}},
                        ]
                    }
                }
                r = await client.post(self.webhook_url, json=payload, timeout=5)
                return r.is_success
        except Exception:
            logger.exception("Feishu send failed")
            return False
