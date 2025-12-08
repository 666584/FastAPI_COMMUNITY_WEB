# controllers/post_controller.py
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy.orm import Session
from models import post_model
from models import user_model
from models.post_model import Post
from models.user_model import User
from typing import Optional
from controllers.ai_chat_controller import summarize_news

ALLOWED_CATEGORIES = ["금리", "환율", "주식", "부동산", "경제정책", "암호화폐"]

def post_to_dict(post: Post) -> dict:
    return {
        "id": post.id,
        "title": post.title,
        "opinion": post.content,
        "time": post.datetime.isoformat() if post.datetime else None,
        "image": post.image,
        "likes": post.likes,
        "comments": post.comments,
        "views": post.views,
        "category": getattr(post, "category", None),
        "url": getattr(post, "url", None),
        "summary":post.summary if hasattr(post, "summary") else None,
    }

def get_post(db: Session, skip: int = 0, limit: int = 20):
    posts = (
        db.query(Post, User.username)
        .join(User, User.id == Post.author_id)
        .order_by(Post.datetime.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for post, username in posts:
        post_dict = post_to_dict(post)
        post_dict["author"] = username
        result.append(post_dict)

    return result

def get_post_by_id(db: Session, post_id: int):
    """
    Post + Author Username 포함한 상세 조회
    """
    post = post_model.get_post_by_id(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="post_not_found")

    user = user_model.get_user_by_id(db, post.author_id)
    username = user.username if user else None
    post_dict = post_to_dict(post)
    post_dict["author"] = username
    return post_dict

def create_post(db: Session, data: dict):
    title = data.get("title")
    content = data.get("content")
    author_id = data.get("author_id")
    image: Optional[str] = data.get("image", None)
    category = data.get("category")
    url: Optional[str] = data.get("url", None)
    summary: Optional[str] = data.get("summary", None)

    # Title validation
    if not title:
        raise HTTPException(status_code=400, detail="missing_title")
    if len(title) > 100:
        raise HTTPException(status_code=400, detail="title_too_long")

    # Content validation
    if not content:
        raise HTTPException(status_code=400, detail="missing_content")
    
    if not author_id:
        raise HTTPException(status_code=400, detail="missing_author_id")

    if image and len(image) > 200:
        raise HTTPException(status_code=400, detail="image_url_too_long")
    
    if category is not None:
        if category not in ALLOWED_CATEGORIES:
            raise HTTPException(status_code=400, detail="invalid_category")
        if len(category) > 50:
            raise HTTPException(status_code=400, detail="category_too_long")
    if not summary:
        summarize_news_result = summarize_news(title=title, opinion=content, url=url)
        summary = summarize_news_result.get("summary", [])
        if not url:
            url = summarize_news_result.get("url", None)
        if not image:
            image = summarize_news_result.get("image_url", None)
    try:
        post = post_model.create_post(
            db=db,
            title=title,
            content=content,
            author_id=author_id,
            image=image,
            category=category,
            url=url,
            summary=summary
        )
    except Exception as e:
        # DB 에러 발생 시 500으로 래핑
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"failed_to_create_post: {str(e)}",
        )

    return {"status_code": 201, "data": post_to_dict(post)}

def update_post(db: Session, post_id: int, data: dict):
    post_item = post_model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")
    
    title: Optional[str] = data.get("title", None)
    content: Optional[str] = data.get("content", None)
    image: Optional[str] = data.get("image", None)
    category: Optional[str] = data.get("category", None)
    url: Optional[str] = data.get("url", None)

    if title is not None and len(title) > 26:
        raise HTTPException(status_code=400, detail="title_too_long")
        
    if category is not None:
        if category not in ALLOWED_CATEGORIES:
            raise HTTPException(status_code=400, detail="invalid_category")
        if len(category) > 50:
            raise HTTPException(status_code=400, detail="category_too_long")
    
    if url is not None and len(url) > 200:
        raise HTTPException(status_code=400, detail="url_too_long")
    
    if url:
        summarize_news_result = summarize_news(title=title or post_item.title, url=url)
        summary = summarize_news_result.get("summary", [])   

    updated_post = post_model.update_post(
        db=db,
        post_id=post_id,
        title=title,
        content=content,
        image=image,
        category=category,
        summary=summary if url else None,
        url=url
    )

    if not updated_post:
        raise HTTPException(status_code=500, detail="failed_to_update_post")
    
    return {"status_code": 200, "data": post_to_dict(updated_post)}

def delete_post(db: Session, post_id: int):
    post_item = post_model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")
    
    ok = post_model.delete_post(db, post_id)
    if not ok:
        raise HTTPException(status_code=500, detail="failed_to_delete_post")

    return {"status_code": 204, "data": "post_deleted_successfully"}

def update_comments_count(db: Session, post_id: int, isComment: bool):
    """
    댓글 개수 변경 컨트롤러
    """
    post_item = post_model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")

    updated_post = post_model.update_comments_count(db, post_id, isComment)

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
    post_item = post_model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")

    updated_post = post_model.update_likes_count(db, post_id, isLike)

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
    post_item = post_model.get_post_by_id(db, post_id)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")

    updated_post = post_model.update_views_count(db, post_id)

    if not updated_post:
        raise HTTPException(status_code=500, detail="failed_to_update_views_count")

    return {
        "status_code": 200,
        "data": f"views_updated_to_{updated_post.views}"
    }