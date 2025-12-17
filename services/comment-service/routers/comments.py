from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from models import Comment
from schemas import CommentCreate, Comment as CommentSchema
import httpx
import os

ISSUE_SERVICE_URL = os.getenv("ISSUE_SERVICE_URL")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")

router = APIRouter(prefix="/api/comments", tags=["comments"])

async def validate_issue(issue_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{ISSUE_SERVICE_URL}/api/issues/{issue_id}")
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid issue ID")

async def validate_user(user_id: str):
    if not user_id:
        return
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{USER_SERVICE_URL}/api/users/{user_id}")
        if resp.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid user ID")

@router.post("/", response_model=CommentSchema, status_code=201)
async def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    await validate_issue(comment.issue_id)
    await validate_user(str(comment.author_id))
    new_comment = Comment(**comment.dict())
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/issue/{issue_id}", response_model=List[CommentSchema])
def get_comments_for_issue(issue_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.issue_id == issue_id).order_by(Comment.created_at).all()

@router.delete("/{comment_id}")
def delete_comment(comment_id: UUID, db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()
    return {"status": "deleted", "id": str(comment_id)}