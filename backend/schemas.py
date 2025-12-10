from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CommentBase(BaseModel):
    user: str
    body: str

class CommentCreate(CommentBase):
    issue_id: int

class Comment(CommentBase):
    id: int
    issue_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class IssueBase(BaseModel):
    title: str
    description: Optional[str] = None
    repository: str

class IssueCreate(IssueBase):
    created_by: str = "anonymous"

class IssueUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class Issue(IssueBase):
    id: int
    status: str
    created_by: str
    created_at: datetime
    # comments: List[Comment] = [] # Optional: include comments in detail view
    
    class Config:
        from_attributes = True
