from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Issue
from schemas import IssueCreate, IssueUpdate, Issue
import httpx
import os

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

router = APIRouter(prefix="/api/issues", tags=["issues"])

async def validate_user(user_id: str):
    if not user_id:
        return
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{USER_SERVICE_URL}/api/users/{user_id}")
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail=f"User {user_id} not found")

@router.post("/", response_model=Issue)
async def create_issue(issue: IssueCreate, db: Session = Depends(get_db)):
    await validate_user(str(issue.creator_id))
    await validate_user(str(issue.assignee_id))
    db_issue = Issue(**issue.dict())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

@router.get("/", response_model=List[Issue])
def list_issues(db: Session = Depends(get_db)):
    return db.query(Issue).all()

@router.get("/{issue_id}", response_model=Issue)
def get_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.issue_id==issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@router.put("/{issue_id}", response_model=Issue)
def update_issue(issue_id: int, update: IssueUpdate, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.issue_id==issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    for k, v in update.dict(exclude_unset=True).items():
        setattr(issue, k, v)
    db.commit()
    db.refresh(issue)
    return issue

@router.delete("/{issue_id}")
def delete_issue(issue_id: int, db: Session = Depends(get_db)):
    issue = db.query(Issue).filter(Issue.issue_id==issue_id).first()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    db.delete(issue)
    db.commit()
    return {"status": "deleted"}