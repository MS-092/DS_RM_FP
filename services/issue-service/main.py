from fastapi import FastAPI
from database import Base, engine
from routers import issues

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Issue Service")
app.include_router(issues.router)