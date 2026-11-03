from pydantic import BaseModel, Field
from uuid import uuid4
from datetime import datetime, timezone


#
## Observation Data Model - Complementary Data for Healthcare Event - (Internal format)
class ObservationData(BaseModel):
    patient_id: str
    observation_type: str
    value: float
    unit: str


#
## Healthcare Event Model
class HealthcareEvent(BaseModel):
    event_id: str = Field(default_factory=lambda:str(uuid4()))
    event_type: str = "observation.created"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    patient_id: str
    data: ObservationData


#
## External Observation Data Model - Unformatted Data from External System
class ExternalObservationData(BaseModel):
    patient_number: str
    test: str
    result: float
    measurement: str