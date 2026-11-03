from aiokafka import AIOKafkaProducer

from app.schemas.events import ObservationEventMessage

import os
import ssl

class KafkaEventProducer:
    def __init__(self):
        self.bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS"
        )
        self.username = os.getenv("KAFKA_USERNAME")
        self.password = os.getenv("KAFKA_PASSWORD")
        self.topic = os.getenv("KAFKA_TOPIC", "observations")

        self.producer = None


    async def start(self):
        ssl_context = ssl.create_default_context()

        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            security_protocol="SASL_SSL",
            sasl_mechanism="SCRAM-SHA-512",
            sasl_plain_username=self.username,
            sasl_plain_password=self.password,
            ssl_context=ssl_context,
        )

        try:
            await self.producer.start()
            print("Kafka conectado com TLS + SCRAM!")
        except Exception as e:
            print(type(e).__name__, repr(e))
            raise

    async def stop(self):
        if self.producer:
            await self.producer.stop()
            self.producer = None


    async def publish_observation(self, event: ObservationEventMessage):
        message = event.model_dump_json().encode("utf-8")

        await self.producer.send_and_wait(
            topic=self.topic,
            value=message
        )