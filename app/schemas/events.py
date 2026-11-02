from pydantic import BaseModel, Field


#
##
class Observation(BaseModel):
    patient_id: str
    observation_type: str
    value: float
    unit: str