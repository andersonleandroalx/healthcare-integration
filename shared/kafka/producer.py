from aiokafka import AIOKafkaProducer

from app.schemas.events import ObservationEventMessage


class KafkaEventProducer:
    def __init__(self, bootstrap_servers="localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None


    async def start(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await self.producer.start()

    async def stop(self):
        if self.producer:
            await self.producer.stop()

    async def publish_observation(self, event: ObservationEventMessage):
        message = event.model_dump_json().encode("utf-8")

        await self.producer.send_and_wait(topic="observation", value=message)