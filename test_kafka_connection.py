import asyncio
import os
import ssl

from dotenv import load_dotenv
from aiokafka import AIOKafkaProducer

load_dotenv()


async def main():
    producer = AIOKafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS"),
        security_protocol="SASL_SSL",
        sasl_mechanism="SCRAM-SHA-512",
        sasl_plain_username=os.getenv("KAFKA_USERNAME"),
        sasl_plain_password=os.getenv("KAFKA_PASSWORD"),
        ssl_context=ssl.create_default_context(),
    )

    try:
        await producer.start()
        print("Kafka connected with TLS + SCRAM!")

        await producer.send_and_wait(
            "observations",
            b'{"message": "Hello from local PC"}'
        )

        print("Message published successfully!")

    finally:
        await producer.stop()


asyncio.run(main())