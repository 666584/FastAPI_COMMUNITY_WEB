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