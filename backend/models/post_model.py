# models/post_model.py
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from database import Base


# 🔹 1) 실제 DB 테이블과 연결되는 ORM 모델
class Post(Base):
    __tablename__ = "posts"  # MySQL에 생성될 테이블 이름

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    author_id = Column(Integer, nullable=False)
    image = Column(String(255), nullable=False)
    datetime = Column(DateTime, default=datetime.now)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    views = Column(Integer, default=0)

def get_posts(db: Session, skip: int = 0, limit: int = 20):
    """
    전체 글 목록 가져오기 (페이징 포함)
    """
    return db.query(Post).offset(skip).limit(limit).all()


def get_post_by_id(db: Session, post_id: int):
    """
    ID로 특정 글 하나 조회
    """
    return db.query(Post).filter(Post.id == post_id).first()


def create_post(
    db: Session,
    title: str,
    content: str,
    author_id: int,
    image: Optional[str] = None,
):   
    """
    새 글 생성
    """
    post = Post(
        title=title,
        content=content,
        author_id=author_id,
        image=image,
        # datetime은 모델에서 default=datetime.now 로 설정되어 있으면 자동 세팅
        # likes / comments / views 도 default=0 이면 자동 세팅
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post


def update_post(
    db: Session,
    post_id: int,
    title: Optional[str] = None,
    content: Optional[str] = None,
    image: Optional[str] = None,
):
    """
    글 수정
    """
    post = get_post_by_id(db, post_id)
    if not post:
        return None

    if title is not None:
        post.title = title
    if content is not None:
        post.content = content
    if image is not None:
        post.image = image
    db.commit()
    db.refresh(post)
    return post


def delete_post(db: Session, post_id: int) -> bool:
    """
    글 삭제
    """
    post = get_post_by_id(db, post_id)
    if not post:
        return False

    db.delete(post)
    db.commit()
    return True
