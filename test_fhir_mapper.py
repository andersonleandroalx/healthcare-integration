from app.schemas.events import ObservationData
from app.services.fhir_mapper import to_fhir_observation

observation = ObservationData(
    patient_id="P-1001",
    observation_type="glucose",
    value=5.3,
    unit="mmol/L"
)

result = to_fhir_observation(observation)
print(result)