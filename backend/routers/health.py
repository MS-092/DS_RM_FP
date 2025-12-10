from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/health", tags=["health"])

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    services: dict

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint for monitoring
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": "connected",
            "api": "running"
        }
    }

@router.get("/ready")
async def readiness_check():
    """
    Kubernetes readiness probe
    """
    return {"ready": True}

@router.get("/live")
async def liveness_check():
    """
    Kubernetes liveness probe
    """
    return {"alive": True}
