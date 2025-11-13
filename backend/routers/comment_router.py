# routers/comment_router.py
from fastapi import APIRouter
from controllers import post_controller as controller

router = APIRouter(prefix="/comments")

@router.get("/{post_id}")
async def get_comments(comment_id: int):
    return controller.get_comments(comment_id)

@router.post("/create", status_code=201)
async def create_comment(post_id: int, data: dict):
    return controller.create_comment(post_id, data)

@router.patch("/{comment_id}/update")
async def update_comment(comment_id: int, data: dict):
    return controller.update_comment(comment_id, data)

@router.delete("/{comment_id}/delete", status_code=204)
async def delete_comment(comment_id: int):
    return controller.delete_post(comment_id)