# controllers/post_controller.py
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from models import post_model as model
from models.post_model import Post

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
    
    title = data.get("title")
    content = data.get("content")
    image = data.get("image")

    if title:
        if len(title) > 26:
            raise HTTPException(status_code=400, detail="title_too_long")
        post_item.title = title 

    if content:
        post_item.content = content

    if image:
        if len(image) > 200:
            raise HTTPException(status_code=400, detail="image_url_too_long")
        post_item.image= image

    db.commit()
    db.refresh(post_item)
    
    return {"status_code": 200, "data": post_item}

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
    댓글 개수 증가/감소 (댓글 추가/삭제 시 호출)
    """
    post_item = model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")

    if isComment:
        post_item.comments += 1
    else:
        post_item.comments = max(0, post_item.comments - 1)

    db.commit()
    db.refresh(post_item)
    
    return {"status_code": 200, "data": "Comment count Updated."}

def update_likes_count(db: Session, post_id: int, islike: bool):
    """
    좋아요 개수 증가/감소
    """
    post_item = model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")

    if islike:
        post_item.likes += 1
    else:
        post_item.likes = max(0, post_item.likes - 1)
    
    db.commit()
    db.refresh(post_item)
    
    return {"status_code": 200, "data": "post_likes_upated_successfully."}

def update_views_count(db: Session, post_id: int):
    """
    조회수 증가
    """
    post_item = model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")

    post_item.views += 1
    db.commit()
    db.refresh(post_item)

    return {"status_code": 200, "data": "post_views_upated_successfully."}