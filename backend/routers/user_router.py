# routers/user_router.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from controllers import user_controllers as controller
from database import get_db  # DB Session 의존성

router = APIRouter(prefix="/users")


@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    단일 유저 조회
    """
    return controller.get_user(db, user_id)


@router.post("/register", status_code=201)
async def create_user(data: dict, db: Session = Depends(get_db)):
    """
    회원 가입
    """
    return controller.create_user(db, data)


@router.post("/login")
async def login(data: dict, db: Session = Depends(get_db)):
    """
    로그인
    """
    return controller.login(db, data)


@router.patch("/change_password")
async def change_password(data: dict, db: Session = Depends(get_db)):
    """
    비밀번호 변경
    """
    return controller.change_password(db, data)


@router.patch("/update_username")
async def update_username(data: dict, db: Session = Depends(get_db)):
    """
    유저네임 변경
    """
    return controller.update_username(db, data)


@router.delete("/delete/{user_id}")
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    회원 삭제
    """
    return controller.delete_user(db, user_id)
