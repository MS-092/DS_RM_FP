from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base

class Issue(Base):
    __tablename__ = "issues"
    issue_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(10), default="medium")
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    status = Column(String(20), default="open")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())