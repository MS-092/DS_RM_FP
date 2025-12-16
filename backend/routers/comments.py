from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from database import get_db
from models import Comment
from schemas import CommentCreate, Comment as CommentSchema

router = APIRouter(prefix="/api/comments", tags=["comments"])

@router.post("/", response_model=CommentSchema, status_code=201)
def create_comment(comment: CommentCreate, db: Session = Depends(get_db)):
    """
    Create a new comment on an issue
    """
    new_comment = Comment(
        issue_id=comment.issue_id,
        content=comment.content, # Schema uses 'content', model uses 'content'
        author_id=comment.author_id
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

@router.get("/issue/{issue_id}", response_model=List[CommentSchema])
def get_comments_for_issue(issue_id: int, db: Session = Depends(get_db)):
    """
    Get all comments for a specific issue
    """
    return db.query(Comment).filter(Comment.issue_id == issue_id).order_by(Comment.created_at).all()

@router.delete("/{comment_id}")
def delete_comment(comment_id: UUID, db: Session = Depends(get_db)):
    """
    Delete a comment
    """
    comment = db.query(Comment).filter(Comment.comment_id == comment_id).first()
    
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    
    db.delete(comment)
    db.commit()
    return {"status": "deleted", "id": str(comment_id)}
