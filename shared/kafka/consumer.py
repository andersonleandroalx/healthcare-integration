import os
import ssl


from aiokafka import AIOKafkaConsumer


class KafkaEventConsumer:

    def __init__(self):
        self.bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        self.username = os.getenv("KAFKA_USERNAME")
        self.password = os.getenv("KAFKA_PASSWORD")
        self.topic = os.getenv("KAFKA_TOPIC", "observations")
        self.consumer = None

    async def start(self):
        ssl_context = ssl.create_default_context()

        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            security_protocol="SASL_SSL",
            sasl_mechanism="SCRAM-SHA-512",
            sasl_plain_username=self.username,
            sasl_plain_password=self.password,
            ssl_context=ssl_context,
            group_id="healthcare-dashboard",
            auto_offset_reset="latest", # enables the dashboard to receive new messages from the moment the consumer begins consuming, without loading the entire history.
        )

        await self.consumer.start()
        print("Kafka Consumer connected with TLS + SCRAM!")

    async def stop(self):
        if self.consumer:
            await self.consumer.stop()
            self.consumer = None

    async def consume(self):
        async for message in self.consumer:
            yield message.value.decode("utf-8")