from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
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

class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"
    repo_id: Optional[int] = None

class IssueCreate(IssueBase):
    creator_id: Optional[UUID] = None
    assignee_id: Optional[UUID] = None

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None

class Issue(IssueBase):
    issue_id: int
    status: str
    creator_id: Optional[UUID]
    assignee_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
