from sqlalchemy import Column, Integer, ForeignKey, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from database import Base

class Comment(Base):
    __tablename__ = "issue_comments"
    comment_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    issue_id = Column(Integer, ForeignKey("issues.issue_id", ondelete="CASCADE"))
    author_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())