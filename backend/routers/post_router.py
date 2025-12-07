# routers/post_router.py
from fastapi import APIRouter, Depends, Body, HTTPException
from sqlalchemy.orm import Session
from database import get_db 
from controllers import post_controller as controller

router = APIRouter(prefix="/posts", tags=["posts"])


# 게시글 목록 조회: GET /posts?skip=0&limit=20
@router.get("/")
async def get_posts(skip: int = 0, limit: int = 20, db: Session = Depends(get_db)):
    return controller.get_post(db, skip=skip, limit=limit)


# 게시글 단일 조회: GET /posts/{post_id}
@router.get("/{post_id}")
async def get_post_by_id(post_id: int, db: Session = Depends(get_db)):
    return controller.get_post_by_id(db, post_id)


# 게시글 생성: POST /posts/create
@router.post("/create", status_code=201)
async def create_post(
    data: dict = Body(...),
    db: Session = Depends(get_db),
):
    return controller.create_post(db, data)


# 게시글 수정: POST /posts/{post_id}/update
@router.post("/{post_id}/update")
async def update_post(
    post_id: int,
    data: dict = Body(...),
    db: Session = Depends(get_db),
):
    return controller.update_post(db, post_id, data)


# 게시글 삭제: DELETE /posts/{post_id}/delete
@router.delete("/{post_id}/delete", status_code=204)
async def delete_post(post_id: int, db: Session = Depends(get_db)):
    return controller.delete_post(db, post_id)


# 좋아요 증가/감소: PATCH /posts/{post_id}/likes?islike=true/false
@router.patch("/{post_id}/likes")
async def update_likes_count(
    post_id: int,
    islike: bool,
    db: Session = Depends(get_db),
):
    return controller.update_likes_count(db, post_id, islike)

# 조회수 증가/감소: PATCH /posts/{post_id}/views
@router.patch("/{post_id}/views")
async def update_views_count(
    post_id: int,
    db: Session = Depends(get_db),
):
    return controller.update_views_count(db, post_id)

# 조회수 조회: GET /posts/{post_id}/views
@router.get("/{post_id}/views")
async def update_views_count(
    post_id: int,
    db: Session = Depends(get_db),
):
    return controller.update_views_count(db, post_id)

# 좋아요 수 조회: GET /posts/{post_id}/likes
@router.get("/{post_id}/likes")
async def update_views_count(
    post_id: int,
    db: Session = Depends(get_db),
):
    return controller.update_views_count(db, post_id)