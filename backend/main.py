from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from prometheus_fastapi_instrumentator import Instrumentator
import httpx
import os

import models
from database import SessionLocal, engine, get_db

# Routers
from routers import issues, comments, repositories

# Create tables (if they don't exist)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="GitForge Backend Gateway")

# CORS configuration
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- RESEARCH OBSERVABILITY ---
# Instruments the app to expose metrics at /metrics for Prometheus
Instrumentator().instrument(app).expose(app)

# Include Routers
app.include_router(issues.router)
app.include_router(comments.router)
app.include_router(repositories.router)

# --- CRITICAL ENDPOINT FOR EXPERIMENTS ---
@app.get("/api/health") # Keeping /api/health to match frontend expectations
def health_check(db: Session = Depends(get_db)):
    """
    Used by the Experiment Controller to measure 'Recovery Time'.
    It attempts a simple DB query. If the node is down (Pod Kill), 
    this will fail, returning 500.
    """
    try:
        # execute a lightweight query to verify DB connectivity
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy", 
            "components": {"database": "connected"}
        }
    except Exception as e:
        # This 503 is the 'Failure' signal the experiment script looks for
        raise HTTPException(status_code=503, detail="Database Unavailable")

# Support both /health (for script) and /api/health (for frontend)
@app.get("/health")
def health_check_root(db: Session = Depends(get_db)):
    return health_check(db)

# --- GITEA PROXY (DISTRIBUTED GIT STORE) ---
# Note: For internal K8s DNS, access 'gitea-service'. For local docker-compose, 'ds_rm_fp-gitea-1' or 'localhost:3000'
GITEA_URL = os.getenv("GITEA_URL", "http://localhost:3000")

@app.api_route("/git/{path_name:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def gitea_proxy(path_name: str, request: Request):
    """
    Proxies requests to the Gitea Cluster.
    This decouples the frontend from the specific Git server instance.
    """
    async with httpx.AsyncClient(base_url=GITEA_URL) as client:
        url = f"/{path_name}"
        
        try:
            # Exclude host header to avoid confusion at target
            headers = dict(request.headers)
            headers.pop("host", None)
            
            rp_req = client.build_request(
                request.method, url,
                headers=headers,
                content=await request.body()
            )
            rp_resp = await client.send(rp_req)
            return JSONResponse(
                content=rp_resp.content, 
                status_code=rp_resp.status_code
            )
        except httpx.ConnectError:
             # Simulates "Service Unavailable" during Gitea node failure experiments
            raise HTTPException(status_code=503, detail="Git Service Unreachable")
