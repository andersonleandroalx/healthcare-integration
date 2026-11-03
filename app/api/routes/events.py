from fastapi import APIRouter, status, HTTPException
from app.schemas.events import ExternalObservationData, HealthcareEvent
from app.services.fhir_mapper import to_fhir_observation
from app. services.observation_mapper import map_external_observation

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
async def create_observation_event(payload: ExternalObservationData):
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
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(error),
        )


    try:
        # Convert internal observation to FHIR
        fhir_observation = to_fhir_observation(observation)

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error converting to FHIR: {str(error)}",
        )
    
    # Validation passed, create the HealthcareEvent
    event = HealthcareEvent(
        patient_id=observation.patient_id,
        data=observation,    
    )

    return {
        "message": "Event Accepted",
        "event": event, # Internal Converted Event
        "fhir": fhir_observation, # FHIR Compliant Observation (Example)
    }