
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi.responses import FileResponse
import asyncio

import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn

from app.api.routes.events import router as events_router
from shared.kafka.producer import KafkaEventProducer
from shared.kafka.consumer import KafkaEventConsumer



#
## Open a connection to Kafka when the application starts and close it when the application shuts down.
@asynccontextmanager
async def lifespan(app: FastAPI):
    producer = None
    consumer_task = None

    kafka_enabled = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
    print("KAFKA_ENABLED =", repr(os.getenv("KAFKA_ENABLED")))

    if kafka_enabled:
        producer = KafkaEventProducer()
        await producer.start()
        app.state.kafka_producer = producer

        consumer_task = asyncio.create_task(kafka_listener())
    else:
        app.state.kafka_producer = None

    try:
        yield
    finally:
        if consumer_task:
            consumer_task.cancel()

            try:
                await consumer_task
            except asyncio.CancelledError:
                pass

        if producer:
            await producer.stop()


# App Data
app = FastAPI(
    title="HealthCare Integration Platform",
    description="A small healthcare event-driven integration platform",
    version="0.1.0",
    lifespan=lifespan
)

connected_clients = []

async def kafka_listener():
    consumer = KafkaEventConsumer()

    try:
        await consumer.start()

        async for message in consumer.consume():
            disconnected = []

            for websocket in connected_clients:
                try:
                    await websocket.send_text(message)
                except Exception:
                    disconnected.append(websocket)

            for websocket in disconnected:
                connected_clients.remove(websocket)

    finally:
        await consumer.stop()


@app.websocket("/ws/observations")
async def observations_websocket(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connected_clients:
            connected_clients.remove(websocket)


#
## Health Check Endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "healthcare-integration-platform"
    }

#
## Dashboard
@app.get("/dashboard")
async def dashboard():
    html_path = Path("app/templates/dashboard.html")
    return FileResponse(html_path)


#
# Router Routes
app.include_router(events_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)