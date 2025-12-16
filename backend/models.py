from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Issue(Base):
    __tablename__ = "issues"

    issue_id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, nullable=True) # Links to Gitea repository ID (optional for now)
    creator_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    assignee_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(20), default="open") # open, in-progress, closed
    priority = Column(String(10), default="medium") # low, medium, high
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class Comment(Base):
    __tablename__ = "issue_comments"

    comment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id = Column(Integer, ForeignKey("issues.issue_id", ondelete="CASCADE"))
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
