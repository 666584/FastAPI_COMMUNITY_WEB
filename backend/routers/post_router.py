# routers/user_router.py
from fastapi import APIRouter
from controllers import post_controller as controller

router = APIRouter(prefix="/posts")

@router.get("/{post_id}")
async def get_post(post_id: int):
    return controller.get_post(post_id)

@router.post("/create", status_code=201)
async def create_post(data: dict):
    return controller.create_post(data)

@router.post("/{post_id}/update")
async def update_post(post_id: int, data: dict):
    return controller.update_post(post_id, data)

@router.delete("/{post_id}/delete", status_code=204)
async def delete_post(post_id: int):
    return controller.delete_post(post_id)

@router.patch("/{post_id}/likes")
async def update_likes_count(post_id: int, islike: bool):
    return controller.update_likes_count(post_id, islike)

@router.patch("/{post_id}/views")
async def update_views_count(post_id: int):
    return controller.update_views_count(post_id)