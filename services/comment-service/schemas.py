from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from uuid import UUID

class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    issue_id: int
    author_id: Optional[UUID] = None

class Comment(CommentBase):
    comment_id: UUID
    issue_id: int
    author_id: Optional[UUID]
    created_at: datetime

    class Config:
        from_attributes = True