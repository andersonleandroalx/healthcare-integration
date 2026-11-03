import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


#
## Example of unformatted data from an external system (Lab result for example)
VALID_PAYLOAD = {
    "patient_number": "P-1001",
    "test": "GLU",
    "result": 5.3,
    "measurement": "mmol/L"
}



#
## Teste Case for the Observation Event Endpoint - Creating Observation Event
def test_create_observation_event():
    # Call the endpoint with valid payload to create an observation event
    response = client.post(
        "/events/observations",
        json=VALID_PAYLOAD
    )

    # Check if the response has the status code 202 (Accepted)
    assert response.status_code == 202

    # Convert the response to JSON and check the content
    data = response.json()

    assert data["message"] == "Event Accepted"
    assert data["event"]["patient_id"] == "P-1001"
    assert data["event"]["data"]["observation_type"] == "glucose"
    assert data["fhir"]["resourceType"] == "Observation"
    assert data["fhir"]["valueQuantity"]["value"] == 5.3

    kafka_message = data["kafka_message"]
    assert kafka_message["event_id"] == data["event"]["event_id"]
    assert kafka_message["event_type"] == "observation.created"
    assert kafka_message["patient_id"] == "P-1001"
    assert kafka_message["data"]["resourceType"] == "Observation"
    assert kafka_message["data"]["valueQuantity"]["value"] == 5.3



#
## Test Case for the Observation Event Endpoint - Unknown Test Code
def test_unknow_test_code():
    # Copy the valid payload and modify the test code to an unknown value
    payload = VALID_PAYLOAD.copy()
    payload["test"] = "XYZ" # Unknown test code

    # Call the endpoint with valid payload to create an observation event
    response = client.post(
        "/events/observations",
        json=payload
    )

    assert response.status_code == 422


#
## Test Case for the Observation Event Endpoint - Invalid Result Value
def test_invalid_result_value():
    payload = VALID_PAYLOAD.copy()
    payload["result"] = "abc"  # Invalid result value (not a number)

    response = client.post(
        "/events/observations",
        json=payload
    )

    assert response.status_code == 422


#
## Test Case for the Observation Event Endpoint - FHIR Conversion Error
def test_fhir_conversion_error(monkeypatch):
    import app.api.routes.events as events

    def simulate_fhir_error(observation):
        raise RuntimeError("Simulated FHIR error")

    monkeypatch.setattr(
        events,
        "to_fhir_observation",
        simulate_fhir_error
    )

    response = client.post(
        "/events/observations",
        json=VALID_PAYLOAD
    )

    assert response.status_code == 500
    assert "Error converting to FHIR" in response.json()["detail"]


#
## Test Case for Health Check Endpoint
def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"