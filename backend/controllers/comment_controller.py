# controllers/comment_controller.py
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from models.comment_model import Comment
import models.comment_model as model
from models.post_model import get_post_by_id

def comment_to_dict(comment: Comment) -> dict:
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "author_id": comment.author_id,
        "content": comment.content,
        "datetime": comment.datetime.isoformat() if comment.datetime else None
    }

def create_comment(db: Session, post_id: int, data: dict):
    author_id = data.get("author_id")
    content = data.get("content")

    # Post ID validation
    if not post_id:
        raise HTTPException(status_code=400, detail="missing_post_id")

    if not get_post_by_id(db, post_id):
        raise HTTPException(status_code=404, detail="post_not_found")
    
    # Author ID validation
    if not author_id:
        raise HTTPException(status_code=400, detail="missing_author_id")

    """
    if not get_user_by_id(db, user_id):
        raise HTTPException(status_code=404, detail="author_not_found")
    """

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
    
    return {"status_code": 201, "data": comment_to_dict(comment)}

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