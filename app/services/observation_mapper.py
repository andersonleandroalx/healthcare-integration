from app.schemas.events import ExternalObservationData, ObservationData


# Convertion Symbols
TEST_MAPPING = {
    "GLU": "glucose",
}


def map_external_observation(payload: ExternalObservationData) -> ObservationData:
    # Receives Payload and try to convert
    observation_type = TEST_MAPPING.get(payload.test)

    # If the test code is not supported, raise an error
    if not observation_type:
        raise ValueError(f"Unsupported test code: {payload.test}")

    return ObservationData(
        patient_id = payload.patient_number,
        observation_type = observation_type,
        value = payload.result,
        unit = payload.measurement
    )