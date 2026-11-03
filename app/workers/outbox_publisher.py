import asyncio
import logging
from datetime import datetime, timezone
from dotenv import load_dotenv

from app.database.connection import SessionLocal
from app.database.models import OutboxEvent
from shared.kafka.producer import KafkaEventProducer
from app.schemas.events import ObservationEventMessage


load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

POLL_INTERVAL = 2


async def publish_pending_events(producer):
    db = SessionLocal()

    try:
        events = (
            db.query(OutboxEvent)
            .filter(OutboxEvent.status == "pending")
            .order_by(OutboxEvent.id)
            .limit(50)
            .all()
        )

        for event in events:
            event_id = event.event_id
            payload = event.payload

            try:
                event_message = ObservationEventMessage.model_validate_json(payload)
                await producer.publish_observation(event_message)

                event.status = "published"
                event.published_at = datetime.now(timezone.utc)
                event.attempts += 1

                db.commit()

                logger.info("Event %s published", event_id)

            except Exception:
                db.rollback()

                failed_event = (
                    db.query(OutboxEvent)
                    .filter(OutboxEvent.event_id == event_id)
                    .first()
                )

                if failed_event:
                    failed_event.attempts += 1
                    db.commit()

                logger.exception("Failed to publish event %s", event_id)

    finally:
        db.close()


async def main():
    producer = KafkaEventProducer()

    try:
        await producer.start()
        logger.info("Outbox Publisher started")

        while True:
            await publish_pending_events(producer)
            await asyncio.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        logger.info("Stopping Outbox Publisher")

    finally:
        await producer.stop()


if __name__ == "__main__":
    asyncio.run(main())