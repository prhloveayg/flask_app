import json
import random
from datetime import datetime
import asyncio
import paho.mqtt.publish as publish

class IOTMessage:
    def __init__(self, clientId, info, value, alert, lng, lat, timestamp):
        self.clientId = clientId
        self.info = info
        self.value = value
        self.alert = alert
        self.lng = lng
        self.lat = lat
        self.timestamp = timestamp

async def publish_message(mqtt_broker, topic, message, qos=2):
    try:
        # 连接到 MQTT 代理服务器
        publish.single(topic, message, hostname=mqtt_broker, qos=qos)

    except Exception as e:
        print(f"Failed to publish message. Error: {e}")

async def worker(device_id, mqtt_broker, topic, client_prefix):
    try:
        client_id = f"{client_prefix}{device_id:04d}"

        while True:
            interval = random.randint(5, 16)
            await asyncio.sleep(interval)

            now = datetime.now()
            value = random.randint(0, 100)
            msg = IOTMessage(
                clientId=client_id,
                info=f"Device Data {now.strftime('%Y/%m/%d %H:%M:%S')}",
                value=value,
                alert=1 if value > 80 else 0,
                lng=119.9 + random.uniform(0, 0.6),
                lat=30.1 + random.uniform(0, 0.4),
                timestamp=int(now.timestamp() * 1000)
            )

            content = json.dumps(msg.__dict__)
            await publish_message(mqtt_broker, topic, content)

    except Exception as e:
        print(e)

async def main():
    devices = 5
    mqtt_server = "mqtt"
    topic = "testapp"
    client_prefix = "device"

    try:
        with open("iot.properties", "r") as file:
            properties = dict(line.strip().split("=") for line in file)

            devices = int(properties.get("devices", devices))
            mqtt_server = properties.get("server", mqtt_server)
            topic = properties.get("topic", topic)
            client_prefix = properties.get("prefix", client_prefix)

        tasks = [worker(device_id=i + 1, mqtt_broker=mqtt_server, topic=topic, client_prefix=client_prefix) for i in range(devices)]
        await asyncio.gather(*tasks)

    except Exception as e:
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
