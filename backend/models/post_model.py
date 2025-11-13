# models/post_model.py
from datetime import datetime
from pydantic import BaseModel

class Post(BaseModel):
    id : int
    title: str
    author_id : int
    content : str
    datetime : datetime
    image : str
    likes : int
    comments : int
    views : int

posts = [
    {"id": 1, "title": "Sample Post", "content": "This is a sample post.", "author_id": 1, "datetime": "2024-01-01T12:00:00", "image": "imageurl.com","likes": 10, "comments": 2, "views": 100},
]

def get_posts():
    return posts.copy()

def get_post_by_id(post_id: int):
    return next((p for p in posts if p["id"] == post_id), None)

def add_post(post: dict):
    posts.append(post)
    return post

def delete_post(post: dict):
    posts.remove(post)
    return post
