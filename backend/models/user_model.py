# models/user_model.py
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from typing import Optional
from database import Base
import bcrypt

saltRounds = 10


# 1) 실제 DB 테이블과 연결되는 ORM 모델
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(10), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # 해시된 비밀번호 저장


# 비밀번호 해시 함수
def hash_pw(raw: str) -> str:
    salt = bcrypt.gensalt(rounds=saltRounds)
    return bcrypt.hashpw(raw.encode("utf-8"), salt).decode("utf-8")


# 전체 사용자 조회 (페이징 포함)
def get_users(db: Session, skip: int = 0, limit: int = 20):
    return db.query(User).offset(skip).limit(limit).all()


# ID로 사용자 조회
def get_user_by_id(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


# 이메일로 사용자 조회
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


# username으로 사용자 조회
def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def get_username_by_id(db: Session, user_id: int) -> Optional[str]:
    user = get_user_by_id(db, user_id)
    return user.username if user else None

# 새 사용자 생성
def create_user(
    db: Session,
    username: str,
    email: str,
    raw_password: str,
):
    """
    새 사용자 생성 (비밀번호는 여기서 해시)
    """
    hashed_pw = hash_pw(raw_password)

    user = User(
        username=username,
        email=email,
        password=hashed_pw,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# 사용자 수정 (필요한 필드만 선택적으로 변경)
def update_user(
    db: Session,
    user_id: int,
    username: Optional[str] = None,
    email: Optional[str] = None,
    raw_password: Optional[str] = None,
):
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    if username is not None:
        user.username = username
    if email is not None:
        user.email = email
    if raw_password is not None:
        user.password = hash_pw(raw_password)

    db.commit()
    db.refresh(user)
    return user


# 사용자 삭제
def delete_user(db: Session, user_id: int) -> bool:
    user = get_user_by_id(db, user_id)
    if not user:
        return False

    db.delete(user)
    db.commit()
    return True