# models/comment_model.py
from datetime import datetime
from pydantic import BaseModel

class Comment(BaseModel):
    id : int
    post_id : int
    author_id : int 
    content : str
    datetime : datetime

comments = [
    {"id": 1, "post_id": 1, "author_id": 2, "content": "Great post!", "datetime": "2024-01-02T14:00:00"},
]

def get_comments():
    return comments.copy()

def get_comments_by_post(post_id: int):
    comments = []
    for comment in comments: 
        if comment[post_id] == post_id:
            comments.append(comment)
    return comments

def get_comment_by_id(comment_id: int):
    return next((c for c in comments if c["id"] == comment_id), None)

def add_comment(comment: dict):
    comments.append(comment)
    return comment

def delete_comment(comment: dict):
    comments.remove(comment)
    return comment