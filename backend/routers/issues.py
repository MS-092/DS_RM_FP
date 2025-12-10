from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models import Issue, Comment
from schemas import IssueCreate, Issue as IssueSchema, CommentCreate, Comment as CommentSchema

router = APIRouter(prefix="/api/issues", tags=["issues"])

@router.post("/", response_model=IssueSchema)
async def create_issue(issue: IssueCreate, db: AsyncSession = Depends(get_db)):
    new_issue = Issue(**issue.model_dump())
    db.add(new_issue)
    await db.commit()
    await db.refresh(new_issue)
    return new_issue

@router.get("/", response_model=List[IssueSchema])
async def list_issues(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Issue))
    return result.scalars().all()

@router.get("/{issue_id}", response_model=IssueSchema)
async def get_issue(issue_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@router.delete("/{issue_id}")
async def delete_issue(issue_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Issue).where(Issue.id == issue_id))
    issue = result.scalar_one_or_none()
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    
    await db.delete(issue)
    await db.commit()
    return {"status": "deleted"}
