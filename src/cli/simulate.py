import asyncio
import json
import random
from datetime import datetime, timezone
import aiomqtt


async def simulate(devices: int = 5, sensors_per_device: int = 2,
                   interval: float = 1.0, host: str = "localhost",
                   port: int = 1883):
    sensor_types = ["temperature", "vibration", "current", "humidity"]
    baselines = {"temperature": 25.0, "vibration": 0.5, "current": 10.0,
                 "humidity": 50.0}
    noise = {"temperature": 1.0, "vibration": 0.05, "current": 0.3,
             "humidity": 2.0}

    async with aiomqtt.Client(hostname=host, port=port) as client:
        while True:
            for d in range(devices):
                for s in range(sensors_per_device):
                    stype = random.choice(sensor_types)
                    base = baselines[stype]
                    n = noise[stype]
                    # Inject anomaly ~2% of the time
                    if random.random() < 0.02:
                        base *= random.choice([3.0, -2.0, 5.0])
                    value = base + random.gauss(0, n)
                    payload = {
                        "device_id": f"dev-{d:03d}",
                        "sensor_id": f"{stype}-{s:02d}",
                        "sensor_type": stype,
                        "value": round(value, 4),
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "unit": "",
                    }
                    await client.publish("sensors/data", json.dumps(payload))
            await asyncio.sleep(interval)


if __name__ == "__main__":
    asyncio.run(simulate())
