from app.schemas.events import ObservationData


#
## LOINC Mapping for Observation Types
LOINC_MAPPING = {
    "glucose": {
        "code": "15074-8",
        "display": "Glucose [Moles/volume] in Serum or Plasma"
    }
}


#
## Function to convert ObservationData to FHIR format
def to_fhir_observation(observation: ObservationData) -> dict:
    """
    Transforms an ObservationData object into a FHIR-compliant observation dictionary. (Example)
    """

    loinc_info = LOINC_MAPPING.get(observation.observation_type)
    if not loinc_info:
        raise ValueError(f"Unsupported observation type: {observation.observation_type}")


    return {
        "resourceType": "Observation", # Identifies the type of resource being represented in FHIR (in this case, an observation).
        "status": "final", # Observation status indicating that the observation is complete and verified.
        "code": {
            "coding": [{ # LOINC identifies what was mesured.
                "system": "http://loinc.org", # The coding system used for the observation code (LOINC in this case).
                "code": loinc_info["code"], # The specific LOINC code representing the observation type (e.g., glucose level).
                "display": loinc_info["display"],
            }],
            "text": observation.observation_type # What is being observed (e.g., glucose level, blood pressure). This is a human-readable description of the observation type.
        },
        "subject": {
            "reference": f"Patient/{observation.patient_id}" # Reference to the patient associated with the observation. It links the observation to a specific patient resource in FHIR.
        },
        "valueQuantity": { # Value of the observation, including the measured value, unit, and a reference to the unit system.
            "value": observation.value,
            "unit": observation.unit,
            "system": "http://unitsofmeasure.org", # Identifies in which system the unit is defined (in this case, the Unified Code for Units of Measure).
            "code": observation.unit
        }
    }