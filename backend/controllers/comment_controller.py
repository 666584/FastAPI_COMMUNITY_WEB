# controllers/comment_controller.py
from fastapi import HTTPException
from datetime import datetime
from controllers.post_controller import update_comments_count
from models.comment_model import Comment, comments

async def get_comments(comment_id: int):
    if comment_id <= 0:
        raise HTTPException(status_code=400, detail="invalid_comment_id")
    comment = next((c for c in comments if c["id"] == comment_id), None)
    if not comment:
        raise HTTPException(status_code=404, detail="comment_not_found")
    return {"status_code": 200, "data": comment} 

async def create_comment(post_id: int, data: dict):
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
    result = update_comments_count(post_id, True)
    if result == 0:
        raise HTTPException(status_code=404, detail="post_not_found")
    return {"status_code": 201, "data": new_comment}

async def update_comment(comment_id: int, data: dict):
    comment = next((c for c in comments if c["id"] == comment_id), None)
    if not comment:
        raise HTTPException(status_code=404, detail="comment_not_found")
    
    content = data.get("content")
    if content:
        comment["content"] = content
        comment["datetime"] = datetime.now().isoformat()
    
    return {"status_code": 200, "data": comment}

async def delete_comment(comment_id: int):
    comment_item = next((c for c in comments if c["id"] == comment_id), None)
    if not comment_item:
        raise HTTPException(status_code=404, detail="comment_not_found")
    
    comments.remove(comment_item)
    result = update_comments_count(comment_item["post_id"], False)
    if result == 0:
        raise HTTPException(status_code=404, detail="post_not_found")
    return {"status_code": 204, "data": "comment_deleted_successfully"}