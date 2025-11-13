# models/user_model.py
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    id : int
    username : str = Field(unique=True, index=True, max_length=10)
    email : EmailStr = Field(unique=True, index=True, max_length=255)
    password : str = Field(unique=True, index=True, min_length=8, max_length=20)
    profile : str = Field(max_length=500)

users = [
    {"id": 1, "username": "alice", "email": "alice@test.com", "password": "Test1#", "profile": "www.test_image.com"},
    {"id": 2, "username": "bob", "email": "bob@test.com", "password": "Test2#", "profile": "www.test_image.com"},
]