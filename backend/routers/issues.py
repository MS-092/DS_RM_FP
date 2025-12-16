from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models import Issue
from schemas import IssueCreate, Issue as IssueSchema, IssueUpdate

router = APIRouter(prefix="/api/issues", tags=["issues"])

@router.post("/", response_model=IssueSchema)
def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    # Create issue from pydantic model
    new_issue = Issue(
        title=issue.title,
        description=issue.description,
        priority=issue.priority,
        repo_id=issue.repo_id,
        creator_id=issue.creator_id,
        assignee_id=issue.assignee_id
    )
    db.add(new_issue)
    db.commit()
    db.refresh(new_issue)
    return new_issue

@router.get("/", response_model=List[IssueSchema])
def list_issues(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Issue).offset(skip).limit(limit).all()

@router.get("/{issue_id}", response_model=IssueSchema)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.issue_id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@router.put("/{issue_id}", response_model=IssueSchema)
def update_issue(issue_id: int, update_data: IssueUpdate, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.issue_id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    # Update fields if provided
    if update_data.title is not None:
        issue.title = update_data.title
    if update_data.description is not None:
        issue.description = update_data.description
    if update_data.status is not None:
        issue.status = update_data.status
    if update_data.priority is not None:
        issue.priority = update_data.priority
        
    db.commit()
    db.refresh(issue)
    return issue

@router.delete("/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.issue_id == issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    db.delete(issue)
    db.commit()
    return {"status": "deleted"}
