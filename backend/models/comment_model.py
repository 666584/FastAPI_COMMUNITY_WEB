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