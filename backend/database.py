from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Connection string for CockroachDB
# Using defaultdb to ensure connectivity without extra setup steps
# Use environment variable if available (e.g., in Kubernetes), otherwise localhost
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "cockroachdb://root@localhost:26257/defaultdb")


# Pool pre-ping is enabled to handle connection drops during Fault Injection experiments
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    pool_pre_ping=True 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
