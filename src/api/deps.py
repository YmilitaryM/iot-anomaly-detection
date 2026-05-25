from src.detection.engine import DetectionEngine
from src.alerting.router import AlertRouter

_detection_engine: DetectionEngine | None = None
_alert_router: AlertRouter | None = None


def get_engine() -> DetectionEngine:
    global _detection_engine
    if _detection_engine is None:
        from src.detection.hard_boundary import HardBoundaryDetector
        from src.detection.statistical import StatisticalDetector
        _detection_engine = DetectionEngine(
            detectors=[HardBoundaryDetector(), StatisticalDetector()]
        )
    return _detection_engine


def set_engine(engine: DetectionEngine) -> None:
    global _detection_engine
    _detection_engine = engine


def get_alert_router() -> AlertRouter:
    global _alert_router
    if _alert_router is None:
        _alert_router = AlertRouter()
    return _alert_router


def set_alert_router(router: AlertRouter) -> None:
    global _alert_router
    _alert_router = router
