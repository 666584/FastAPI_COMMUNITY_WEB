# models/user_model.py
from pydantic import BaseModel, EmailStr, Field
import bcrypt

saltRounds = 10

class User(BaseModel):
    id : int
    username : str = Field(unique=True, index=True, max_length=10)
    email : EmailStr = Field(unique=True, index=True, max_length=255)
    password : str = Field(unique=True, index=True, min_length=8, max_length=20)
    profile : str = Field(max_length=500)

def hash_pw(raw: str) -> str:
    salt = bcrypt.gensalt(rounds=saltRounds)
    return bcrypt.hashpw(raw.encode("utf-8"), salt).decode("utf-8")

users = [
    {"id": 1, "username": "alice", "email": "alice@test.com", "password": hash_pw("Test1#"), "profile": "www.test_image.com"},
    {"id": 2, "username": "bob", "email": "bob@test.com", "password": hash_pw("Test2#"), "profile": "www.test_image.com"},
]

# 모든 사용자 조회
def get_users():
    return users.copy()  # 외부에서 수정 방지

# ID로 사용자 조회
def get_user_by_id(user_id: int):
    return next((u for u in users if u["id"] == user_id), None)

# 이메일로 사용자 조회
def get_user_by_email(email: str):
    return next((u for u in users if u["email"] == email), None)

def get_user_by_username(username: str):
    return next((u for u in users if u["username"] == username), None)

# 새 사용자 추가
def add_user(user: dict):
    users.append(user)
    return user

def delete_user(user: dict):
    users.remove(user)
    return user
