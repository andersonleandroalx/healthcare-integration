from fastapi import APIRouter, status, HTTPException, Request, Depends
from app.schemas.events import ExternalObservationData, HealthcareEvent, ObservationEventMessage
from app.services.fhir_mapper import to_fhir_observation
from app.services.observation_mapper import map_external_observation

from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.models import OutboxEvent


#
## Router Data - For Events
router = APIRouter(
        prefix="/events",
        tags=["events"]
    )


# Example of unformatted data from an external system
PAYLOAD_EXAMPLE = {
    "patient_number": "P-1001",
    "test": "GLU",
    "result": 5.3,
    "measurement": "mmol/L"
    }


#
## Observation Event Endpoint
@router.post("/observations",status_code=status.HTTP_202_ACCEPTED)
async def create_observation_event(payload: ExternalObservationData, db: Session = Depends(get_db)):
    """
        - Receives data from third parties in JSON format
        - Validates and converts it into the internal model
        - Converts it into the FHIR model
        - Responds in a more structured format, containing both the internal event and the FHIR model
    """
    try:
        # Map the external test
        observation = map_external_observation(payload)

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        )
    
    # Validation passed, create the HealthcareEvent
    event = HealthcareEvent(
        patient_id=observation.patient_id,
        data=observation,    
    )

    

    try:
        # Convert internal observation to FHIR
        fhir_observation = to_fhir_observation(observation)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error converting to FHIR: {str(error)}",
        )
    
    

    # Create the message that will be published to Kafka
    kafka_message = ObservationEventMessage(
        event_id = event.event_id,
        event_type = event.event_type,
        timestamp = event.timestamp,
        patient_id = event.patient_id,
        data = fhir_observation,
    )

    # Trying to save the event in the Outbox table for later processing
    try:
        # TODO: Implement idempotency using an external request_id.
        # Prevent duplicate events when the laboratory retries a request.
        outbox_event = OutboxEvent(
            event_id=kafka_message.event_id,
            payload=kafka_message.model_dump_json(),
            status="pending"
        )

        db.add(outbox_event)
        db.commit()
        print("Event saved in Outbox")
    
    except Exception as error:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to save event in Outbox"
        )

    return {
        "message": "Event Accepted",
        "event": event, # Internal Converted Event
        "fhir": fhir_observation, # FHIR Compliant Observation (Example)
        "kafka_message": kafka_message, # Kafka Message Format
    }

