# routers/user_router.py
from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter(prefix="/posts")

post = [
    {"id": 1, "title": "Sample Post", "content": "This is a sample post.", "author_id": 1, "datetime": "2024-01-01T12:00:00", "image": "imageurl.com","likes": 10, "comments": 2, "views": 100},
]

@router.get("/{post_id}")
def get_post(post_id: int):
    if post_id <= 0:
        raise HTTPException(status_code=400, detail="invalid_post_id")
    return {"status_code": 200, "data": post}

@router.post("/create", status_code=201)
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

@router.post("/{post_id}/update")
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

@router.delete("/{post_id}/delete", status_code=204)
def delete_post(post_id: int):
    post_item = next((p for p in post if p["id"] == post_id), None)
    if not post_item:
        raise HTTPException(status_code=404, detail="post_not_found")
    
    post.remove(post_item)
    return {"status_code": 204, "data": "post_deleted_successfully"}

# update post comments count when comment is created or deleted