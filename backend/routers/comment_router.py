# routers/comment_router.py
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from database import get_db 
from controllers import comment_controller as controller

router = APIRouter(prefix="/comments")

@router.get("/{post_id}")
async def get_comments(comment_id: int):
    return controller.get_comments(comment_id)

@router.post("/{post_id}/create", status_code=201)
async def create_comment(
    post_id: int, 
    data: dict = Body(...),
    db: Session = Depends(get_db)):
    return controller.create_comment(db, post_id, data)

@router.patch("/{comment_id}/update")
async def update_comment(
    comment_id: int, 
    data: dict= Body(...),
    db: Session = Depends(get_db)):
    return controller.update_comment(db, comment_id, data)

@router.delete("/{comment_id}/delete", status_code=204)
async def delete_comment(comment_id: int,  db: Session = Depends(get_db)):
    return controller.delete_comment(db, comment_id)