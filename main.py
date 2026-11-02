from fastapi import FastAPI
import uvicorn

# App Data
app = FastAPI(
    title="HealthCare Integration Platform",
    description="A small healthcare event-driven integration platform",
    version="0.1.0",
)


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "healthcare-integration-platform"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)