
from contextlib import asynccontextmanager
import os

from fastapi import FastAPI
import uvicorn

from app.api.routes.events import router as events_router
from shared.kafka.producer import KafkaEventProducer


#
## Open a connection to Kafka when the application starts and close it when the application shuts down.
@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = None

    # It only connects to Kafka when enabled
    kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"

    if kafka_enabled:
        producer = KafkaEventProducer()
        await producer.start()
        app.state.kafka_producer = producer
    else:
        app.state.kafka_producer = None

    try:
        yield
    finally:
        if producer:
            await producer.stop()


# App Data
app = FastAPI(
    title="HealthCare Integration Platform",
    description="A small healthcare event-driven integration platform",
    version="0.1.0",
)


#
## Health Check Endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "healthcare-integration-platform"
    }

# Router Routes
app.include_router(events_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)