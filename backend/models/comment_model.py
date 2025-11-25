# models/comment_model.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from database import Base
from models.post_model import update_comments_count

class Comment(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    author_id = Column(Integer, nullable=False)
    post_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    datetime = Column(DateTime, default=datetime.now)

def get_comments_by_post_id(db: Session, post_id: int, skip: int = 0, limit: int = 20):
    """
    특정 게시글(post_id)의 전체 댓글 ORM 객체 반환
    """
    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.datetime.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    
    return comments

def get_comment_by_id(db: Session, comment_id: int):

    return db.query(Comment).filter(Comment.id == comment_id).first()

def create_comment(
    db: Session,
    post_id: int,
    author_id: int,
    content: str
):
    """
    댓글 생성
    """
    comment = Comment(
        post_id=post_id,
        content=content,
        author_id = author_id,
    )
    update_comments_count(db, post_id, True)
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

def delete_comment(db: Session, comment_id: int) -> bool:
    """
    댓글 삭제
    """
    comment = get_comment_by_id(db, comment_id)
    if not comment:
        return False
    post_id = comment.post_id
    update_comments_count(db, post_id, False)
    db.delete(comment)
    db.commit()
    return True