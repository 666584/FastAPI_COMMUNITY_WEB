# routers/comment_router.py
from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter(prefix="/comments")

comments = [
    {"id": 1, "post_id": 1, "author_id": 2, "content": "Great post!", "datetime": "2024-01-02T14:00:00"},
]

@router.get("/{comment_id}")
def get_comment(comment_id: int):
    if comment_id <= 0:
        raise HTTPException(status_code=400, detail="invalid_comment_id")
    comment = next((c for c in comments if c["id"] == comment_id), None)
    if not comment:
        raise HTTPException(status_code=404, detail="comment_not_found")
    return {"status_code": 200, "data": comment} 

@router.post("/{post_id}/create", status_code=201)
def create_comment(post_id: int, data: dict):
    author_id = data.get("author_id")
    content = data.get("content")

    # Post ID validation
    if not post_id:
        raise HTTPException(status_code=400, detail="missing_post_id")

    # Author ID validation
    if not author_id:
        raise HTTPException(status_code=400, detail="missing_author_id")

    # Content validation
    if not content:
        raise HTTPException(status_code=400, detail="missing_content")

    new_comment = {
        "id": len(comments) + 1,
        "post_id": post_id,
        "author_id": author_id,
        "content": content,
        "datetime": datetime.now().isoformat()
    }
    comments.append(new_comment)
    return {"status_code": 201, "data": new_comment}

@router.patch("/{comment_id}/update")
def update_comment(comment_id: int, data: dict):
    comment = next((c for c in comments if c["id"] == comment_id), None)
    if not comment:
        raise HTTPException(status_code=404, detail="comment_not_found")
    
    content = data.get("content")
    if content:
        comment["content"] = content
        comment["datetime"] = datetime.now().isoformat()
    
    return {"status_code": 200, "data": comment}

@router.delete("/{comment_id}/delete", status_code=204)
def delete_comment(comment_id: int):
    comment_item = next((c for c in comments if c["id"] == id), None)
    if not comment_item:
        raise HTTPException(status_code=404, detail="comment_not_found")
    
    comments.remove(comment_item)
    return {"status_code": 204, "data": "comment_deleted_successfully"}

# update post comments count when comment is created or deleted