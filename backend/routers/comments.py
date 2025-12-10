from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from database import get_db
from models import Comment
from schemas import CommentCreate, Comment as CommentSchema

router = APIRouter(prefix="/api/comments", tags=["comments"])

@router.post("/", response_model=CommentSchema, status_code=201)
async def create_comment(comment: CommentCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new comment on an issue
    """
    new_comment = Comment(**comment.model_dump())
    db.add(new_comment)
    await db.commit()
    await db.refresh(new_comment)
    return new_comment

@router.get("/issue/{issue_id}", response_model=List[CommentSchema])
async def get_comments_for_issue(issue_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get all comments for a specific issue
    """
    result = await db.execute(
        select(Comment).where(Comment.issue_id == issue_id).order_by(Comment.created_at)
    )
    return result.scalars().all()

@router.delete("/{comment_id}")
async def delete_comment(comment_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a comment
    """
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    await db.delete(comment)
    await db.commit()
    return {"status": "deleted", "id": comment_id}
