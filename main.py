from fastapi import FastAPI
import uvicorn

from app.api.routes.events import router as events_router

# App Data
app = FastAPI(
    title="HealthCare Integration Platform",
    description="A small healthcare event-driven integration platform",
    version="0.1.0",
)


#
## Health Check Endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "healthcare-integration-platform"
    }

# Router Routes
app.include_router(events_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8888, reload=True)