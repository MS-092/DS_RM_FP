from fastapi import FastAPI
from routers import repositories

app = FastAPI(title="Repository Service")
app.include_router(repositories.router)