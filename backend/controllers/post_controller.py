# controllers/post_controller.py
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from models import post_model as model
from models.post_model import Post
from typing import Optional

def post_to_dict(post: Post) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "datetime": post.datetime.isoformat() if post.datetime else None,
        "image": post.image,
        "likes": post.likes,
        "comments": post.comments,
        "views": post.views,
    }

def get_post(db: Session, skip: int = 0, limit: int = 20):
    posts = model.get_posts(db, skip=skip, limit=limit)
    return [post_to_dict(p) for p in posts]

def create_post(db: Session, data: dict):
    title = data.get("title")
    content = data.get("content")
    author_id = data.get("author_id")
    image = data.get("image")

    # Title validation
    if not title:
        raise HTTPException(status_code=400, detail="missing_title")
    if len(title) > 26:
        raise HTTPException(status_code=400, detail="title_too_long")

    # Content validation
    if not content:
        raise HTTPException(status_code=400, detail="missing_content")
    
    if not author_id:
        raise HTTPException(status_code=400, detail="missing_author_id")

    if image and len(image) > 200:
        raise HTTPException(status_code=400, detail="image_url_too_long")
    
    try:
        post = model.create_post(
            db=db,
            title=title,
            content=content,
            author_id=author_id,
            image=image,
        )
    except Exception as e:
        # DB 에러 발생 시 500으로 래핑
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed_to_create_post: {str(e)}",
        )

    return {"status_code": 201, "data": post_to_dict(post)}

def update_post(db: Session, post_id: int, data: dict):
    post_item = model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")
    
    title: Optional[str] = data.get("title", None)
    content: Optional[str] = data.get("content", None)
    image: Optional[str] = data.get("image", None)

    if title is not None and len(title) > 26:
            raise HTTPException(status_code=400, detail="title_too_long")
        
    if image is not None and len(image) > 200:
            raise HTTPException(status_code=400, detail="image_url_too_long")
    
    updated_post = model.update_post(
        db=db,
        post_id=post_id,
        title=title,
        content=content,
        image=image
    )

    if not updated_post:
        raise HTTPException(status_code=500, detail="failed_to_update_post")
    
    return {"status_code": 200, "data": post_to_dict(updated_post)}

def delete_post(db: Session, post_id: int):
    post_item = model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")
    
    ok = model.delete_post(db, post_id)
    if not ok:
        raise HTTPException(status_code=500, detail="failed_to_delete_post")

    return {"status_code": 204, "data": "post_deleted_successfully"}

def update_comments_count(db: Session, post_id: int, isComment: bool):
    """
    댓글 개수 변경 컨트롤러
    """
    post_item = model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")

    updated_post = model.update_comments_count(db, post_id, isComment)

    if not updated_post:
        raise HTTPException(status_code=500, detail="failed_to_update_comment_count")

    return {
        "status_code": 200,
        "data": f"comment_count_updated_to_{updated_post.comments}"
    }

def update_likes_count(db: Session, post_id: int, isLike: bool):
    """
    좋아요 개수 변경 컨트롤러
    """
    post_item = model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")

    updated_post = model.update_likes_count(db, post_id, isLike)

    if not updated_post:
        raise HTTPException(status_code=500, detail="failed_to_update_like_count")

    return {
        "status_code": 200,
        "data": f"like_count_updated_to_{updated_post.likes}"
    }

def update_views_count(db: Session, post_id: int):
    """
    조회수 증가 컨트롤러
    """
    post_item = model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")

    updated_post = model.update_views_count(db, post_id)

    if not updated_post:
        raise HTTPException(status_code=500, detail="failed_to_update_views_count")

    return {
        "status_code": 200,
        "data": f"views_updated_to_{updated_post.views}"
    }