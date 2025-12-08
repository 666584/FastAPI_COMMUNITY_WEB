# controllers/comment_controller.py
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from models.comment_model import Comment
import models.comment_model as model
from models.post_model import get_post_by_id
from typing import Optional
from models.user_model import get_user_by_id, get_username_by_id
from controllers.post_controller import update_comments_count

def comment_to_dict(db: Session, comment: Comment) -> dict:
    return {
        "id": comment.id,
        "author": get_username_by_id(db, comment.author_id) if comment.author_id else "익명",
        "content": comment.content,
        "time": comment.datetime.isoformat() if comment.datetime else None
    }

def get_comments(db: Session, post_id: int):
    # DB에서 댓글 목록 가져오기
    comments = model.get_comments_by_post_id(db, post_id)

    # dict 형태로 변환
    return [comment_to_dict(db, c) for c in comments]

def create_comment(db: Session, data: dict):
    author_id: Optional[int] = data.get("author_id")
    content = data.get("content")
    post_id = data.get("post_id")

    # Post ID validation
    if not post_id:
        raise HTTPException(status_code=400, detail="missing_post_id")

    if not get_post_by_id(db, post_id):
        raise HTTPException(status_code=404, detail="post_not_found")
    
    if author_id:
        if not get_user_by_id(db, author_id):
            raise HTTPException(status_code=404, detail="author_not_found")

    # Content validation
    if not content:
        raise HTTPException(status_code=400, detail="missing_content")

    try: 
        comment = model.create_comment(
            db=db,
            post_id = post_id,
            author_id = author_id,
            content = content,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed_to_create_comment: {str(e)}",
        )
    
    return {"status_code": 201, "data": comment_to_dict(db, comment)}

def update_comment(db: Session, comment_id: int, data: dict):
    comment = model.get_comment_by_id(db, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="comment_not_found")
    
    content = data.get("content")
    if content:
        comment.content = content
        comment.datetime = datetime.now().isoformat()
    
    return {"status_code": 200, "data": comment}

def delete_comment(db: Session, comment_id: int):
    comment_item = model.get_comment_by_id(db, comment_id)
    if not comment_item:
        raise HTTPException(status_code=404, detail="comment_not_found")
    
    ok = model.delete_comment(db, comment_item)
    if not ok:
        raise HTTPException(status_code=500, detail="failed_to_delete_comment")

    return {"status_code": 204, "data": "comment_deleted_successfully"}