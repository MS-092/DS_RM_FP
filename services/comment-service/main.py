from fastapi import FastAPI
from database import Base, engine
from routers import comments

Base.metadata.create_all(bind=engine)
app = FastAPI(title="Comment Service")
app.include_router(comments.router)