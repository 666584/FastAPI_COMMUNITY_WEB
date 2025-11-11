# routers/user_router.py
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/users")

users = [
    {"id": 1, "name": "Alice", "email": "alice@test.com"},
    {"id": 2, "name": "Bob", "email": "bob@test.com"},
]

@router.get("/{user_id}")
def get_user(user_id: int):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="invalid_user_id")
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")
    return {"status_code": 200, "data": user}

@router.post("/", status_code=201)
def create_user(data: dict):
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        raise HTTPException(status_code=400, detail="missing_required_fields")
    if any(u["email"] == email for u in users):
        # 필요시 409로 교체 가능
        raise HTTPException(status_code=403, detail="email_already_exists")

    new_user = {"id": len(users) + 1, "name": name, "email": email}
    users.append(new_user)
    return {"status_code": 201, "data": new_user}

@router.post("/login")
def login(data: dict):
    email = data.get("email")
    if not email:
        raise HTTPException(status_code=400, detail="missing_email")
    user = next((u for u in users if u["email"] == email), None)
    if not user:
        raise HTTPException(status_code=401, detail="unauthorized")
    return {"status_code": 200, "data": {"user_id": user["id"], "name": user["name"]}}