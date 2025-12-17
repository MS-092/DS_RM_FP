from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[str] = "medium"

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