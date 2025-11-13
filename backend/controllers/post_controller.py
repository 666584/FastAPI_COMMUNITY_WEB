# controllers/post_controller.py
from fastapi import HTTPException
from datetime import datetime
from pydantic import BaseModel
from comment_controller import Comment

class Post(BaseModel):
    id : int
    title: str
    author_id : int
    content : str
    datetime : datetime
    image : str
    likes : int
    comments : int
    views : int

post = [
    {"id": 1, "title": "Sample Post", "content": "This is a sample post.", "author_id": 1, "datetime": "2024-01-01T12:00:00", "image": "imageurl.com","likes": 10, "comments": 2, "views": 100},
]

def get_post(post_id: int):
    if post_id <= 0:
        raise HTTPException(status_code=400, detail="invalid_post_id")
    return {"status_code": 200, "data": post}

def create_post(data: dict):
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
    
    new_post = {
        "id": len(post) + 1,
        "title": title,
        "content": content,
        "author_id": author_id,
        "datetime": datetime.now().isoformat(),
        "image": image,
        "likes": 0,
        "comments": 0,
        "views": 0
    }

    post.append(new_post)
    return {"status_code": 201, "data": new_post}

def update_post(post_id: int, data: dict):
    post_item = next((p for p in post if p["id"] == post_id), None)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")
    
    title = data.get("title")
    content = data.get("content")
    image = data.get("image")

    if title:
        if len(title) > 26:
            raise HTTPException(status_code=400, detail="title_too_long")
        post_item["title"] = title

    if content:
        post_item["content"] = content

    if image:
        if len(image) > 200:
            raise HTTPException(status_code=400, detail="image_url_too_long")
        post_item["image"] = image

    return {"status_code": 200, "data": post_item}

def delete_post(post_id: int):
    post_item = next((p for p in post if p["id"] == post_id), None)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")
    
    post.remove(post_item)
    return {"status_code": 204, "data": "post_deleted_successfully"}

# update post comments count when comment is created or deleted
def update_comments_count(post_id: int, isComment: bool):
    post_item = next((p for p in post if p["id"] == post_id), None)
    if not post_item:
        return 0
    if isComment:
        post_item["comments"] += 1
    elif isComment:
        post_item["comments"] -= 1
    return "Comment count Updated."

def update_likes_count(post_id: int, islike: bool):
    post_item = next((p for p in post if p["id"] == post_id), None)
    
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")
    if islike:
        post_item['likes'] += 1
    elif not islike:
        post_item['likes'] -= 1
    
    return {"status_code": 204, "data": "post_likes_upated_successfully."}

def update_views_count(post_id: int):
    post_item = next((p for p in post if p["id"] == post_id), None)
    
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")
    post_item['views'] += 1
    
    return {"status_code": 204, "data": "post_views_upated_successfully."}