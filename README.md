# Healthcare Integration Platform

A Python-based healthcare integration PoC demonstrating how clinical observations can be validated, transformed into FHIR-style resources, persisted reliably, and distributed through Apache Kafka.

The project explores event-driven architecture, asynchronous processing, secure messaging, and real-time monitoring.

## Architecture

```text
                    ┌──────────────────────┐
                    │     HTTP Client      │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    FastAPI Backend   │
                    │ Validation & Mapping │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    SQLite Outbox     │
                    │   Persistent Events  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │   Outbox Publisher   │
                    │   Background Worker  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Apache Kafka      │
                    │   observations topic │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Kafka Consumer    │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │ WebSocket Dashboard  │
                    │  Real-time Events    │
                    └──────────────────────┘
```

## Key Features

- **REST API:** Receives healthcare observation data through FastAPI.
- **Data validation:** Validates incoming payloads before processing.
- **FHIR-style mapping:** Transforms incoming data into an Observation resource structure.
- **Transactional Outbox pattern:** Persists events in SQLite before publishing them to Kafka.
- **Background publishing:** A dedicated worker periodically checks for pending events and publishes them.
- **Apache Kafka:** Distributes healthcare events through a dedicated topic.
- **Secure Kafka communication:** Uses TLS encryption and SASL/SCRAM-SHA-512 authentication.
- **Kafka Consumer:** Consumes events asynchronously.
- **WebSocket integration:** Pushes incoming Kafka messages to the dashboard in real time.
- **Event monitoring:** Displays submitted observations and consumed Kafka messages.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| FastAPI | REST API and WebSocket server |
| Pydantic | Data validation and serialization |
| SQLite | Persistent event storage |
| SQLAlchemy | Database access |
| Apache Kafka | Event streaming and messaging |
| aiokafka | Asynchronous Kafka producer and consumer |
| WebSocket | Real-time communication |
| HTML, CSS, JavaScript | Monitoring dashboard |
| python-dotenv | Environment configuration |

## Event Flow

1. A client submits an observation to the FastAPI endpoint.
2. The backend validates the incoming data and maps it into a FHIR-style Observation resource.
3. The event is persisted in the SQLite Outbox with a pending status.
4. The Outbox Publisher retrieves pending events in the background.
5. Events are published to the Kafka `observations` topic.
6. Successfully published events are marked as published in the database.
7. The Kafka Consumer receives new messages.
8. Messages are forwarded through WebSocket connections to the monitoring dashboard.

## Example Request

**Endpoint**

`POST /events/observations`

**Request body**

```json
{
  "patient_number": "P-1001",
  "test": "GLU",
  "result": 5.3,
  "measurement": "mmol/L"
}
```

The backend validates the payload and generates an event containing an Observation resource.

**Example event structure**

```json
{
  "event_id": "b0d52516-...",
  "event_type": "observation.created",
  "patient_id": "P-1001",
  "timestamp": "2026-11-03T12:37:12Z",
  "data": {
    "resourceType": "Observation",
    "status": "final",
    "subject": {
      "reference": "Patient/P-1001"
    }
  }
}
```

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/healthcare-integration.git
cd healthcare-integration
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
KAFKA_BOOTSTRAP_SERVERS=your-kafka-host:9094
KAFKA_USERNAME=your-kafka-username
KAFKA_PASSWORD=your-kafka-password
KAFKA_TOPIC=observations
KAFKA_ENABLED=true
```

The Kafka broker must be configured to accept TLS connections and SASL/SCRAM-SHA-512 authentication.

**Never commit your `.env` file or expose credentials in the repository.**

### 5. Start the FastAPI application

```bash
uvicorn main:app --host 0.0.0.0 --port 8888 --reload
```

### 6. Start the Outbox Publisher

In a separate terminal:

```bash
python -m app.workers.outbox_publisher
```

### 7. Open the dashboard

Navigate to:

```text
http://localhost:8888/dashboard
```

Submit an observation and monitor its progress through the Outbox and Kafka Consumer.

## Security Considerations

- Kafka connections use TLS encryption.
- SASL/SCRAM-SHA-512 is used for client authentication.
- Credentials are loaded from environment variables.
- Sensitive configuration should not be committed to version control.

## Project Goals

This project was built as a practical exploration of healthcare interoperability and event-driven backend architecture.

It focuses on concepts such as:

- Reliable event publishing with the Transactional Outbox pattern.
- Asynchronous event processing.
- Producer and consumer communication.
- Secure integration with external messaging infrastructure.
- Real-time updates through WebSockets.
- Separation of API responsibilities and background processing.

## Disclaimer

This is an educational Proof of Concept (PoC), not a production-ready healthcare system.

It does not implement a complete HL7 FHIR specification, production-grade patient data security, or regulatory compliance requirements. No real patient data should be used.

---

**Built with Python, FastAPI, SQLite, Apache Kafka and WebSockets.**
