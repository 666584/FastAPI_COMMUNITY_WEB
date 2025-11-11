# routers/user_router.py
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/users")

users = [
    {"id": 1, "username": "alice", "email": "alice@test.com"},
    {"id": 2, "username": "bob", "email": "bob@test.com"},
]

@router.get("/{user_id}")
def get_user(user_id: int):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="invalid_user_id")
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")
    return {"status_code": 200, "data": user}

@router.post("/register", status_code=201)
def create_user(data: dict):
    username = data.get("username")
    email = data.get("email")
    password1 = data.get("password1")
    password2 = data.get("password2")
    profile = data.get("profile")

    # Profile validation
    if not profile:
        raise HTTPException(status_code=400, detail="missing_profile")
    if profile and len(profile) > 500:
        raise HTTPException(status_code=400, detail="profile_too_long")
    
    # Username validation
    if not username:
        raise HTTPException(status_code=400, detail="missing_username")
    if any(u["username"] == username for u in users):
        raise HTTPException(status_code=403, detail="username_already_exists")
    if " " in username:
        raise HTTPException(status_code=400, detail="username_contains_space")
    if len(username) > 10:
        raise HTTPException(status_code=400, detail="username_too_long")
    if username.lower() in {"admin", "root", "system"}:
        raise HTTPException(status_code=400, detail="username_reserved")

    # Password complexity checks
    if not password1:
        raise HTTPException(status_code=400, detail="missing_password")
    if not password2:
        raise HTTPException(status_code=400, detail="missing_password_confirmation")
    if password1 != password2:
        raise HTTPException(status_code=400, detail="passwords_do_not_match")    
    if len(password1) < 8:
        raise HTTPException(status_code=400, detail="password_too_short")
    if len(password1) > 20:
        raise HTTPException(status_code=400, detail="password_too_long")
    if " " in password1:
        raise HTTPException(status_code=400, detail="password_contains_space")
    if not any(c.islower() for c in password1):
        raise HTTPException(status_code=400, detail="password_missing_lowercase")
    if not any(c.isupper() for c in password1):
        raise HTTPException(status_code=400, detail="password_missing_uppercase")
    if not any(c.isdigit() for c in password1):
        raise HTTPException(status_code=400, detail="password_missing_digit")
    if not any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for c in password1):
        raise HTTPException(status_code=400, detail="password_missing_special_character")
    
    # Email validation
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="invalid_email_format")
    if len(email) > 254:
        raise HTTPException(status_code=400, detail="email_too_long")
    if any(u["email"] == email for u in users):
        raise HTTPException(status_code=403, detail="email_already_exists")
    if email.startswith(".") or email.endswith("."):
        raise HTTPException(status_code=400, detail="email_invalid_format")
    if " " in email:
        raise HTTPException(status_code=400, detail="email_contains_space")
    if ".." in email:   
        raise HTTPException(status_code=400, detail="email_invalid_format")
    if email.count("@") != 1:
        raise HTTPException(status_code=400, detail="email_invalid_format")
    domain_part = email.split("@")[1]
    if domain_part.startswith("-") or domain_part.endswith("-"):
        raise HTTPException(status_code=400, detail="email_invalid_format")
    if any(c in "(),:;<>[]\\ " for c in email):
        raise HTTPException(status_code=400, detail="email_invalid_characters")
    if not all(ord(c) < 128 for c in email):
        raise HTTPException(status_code=400, detail="email_non_ascii_characters") 
 
    new_user = {"id": len(users) + 1, "username": username, "email": email, "password": password1, "profile": profile}
    users.append(new_user)
    return {"status_code": 201, "data": new_user}

@router.post("/login")
def login(data: dict):
    email = data.get("email")
    password = data.get("password")

    if not email:
        raise HTTPException(status_code=400, detail="missing_email")
    if not isinstance(email, str) or "@" not in email:
        raise HTTPException(status_code=400, detail="invalid_email_format")
    if len(email) > 254:
        raise HTTPException(status_code=400, detail="email_too_long")
    if len(email) < 5:
        raise HTTPException(status_code=400, detail="email_too_short")
    
    user = next((u for u in users if u["email"] == email), None)
    if not user:
        raise HTTPException(status_code=401, detail="unauthorized")
    if not password:
        raise HTTPException(status_code=400, detail="missing_password")
    if password != user["password"]:
        raise HTTPException(status_code=401, detail="unauthorized")

    return {"status_code": 200, "data": {"user_id": user["id"], "username": user["username"]}}

@router.patch("/change_password")
def change_password(data: dict): 
    user_id = data.get("user_id")
    password1 = data.get("password1")
    password2 = data.get("password2")
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")   
    
    # Password complexity checks
    if not password1:
        raise HTTPException(status_code=400, detail="missing_password")
    if not password2:
        raise HTTPException(status_code=400, detail="missing_password_confirmation")
    if password1 != password2:
        raise HTTPException(status_code=400, detail="passwords_do_not_match")    
    if len(password1) < 8:
        raise HTTPException(status_code=400, detail="password_too_short")
    if len(password1) > 20:
        raise HTTPException(status_code=400, detail="password_too_long")
    if " " in password1:
        raise HTTPException(status_code=400, detail="password_contains_space")
    if not any(c.islower() for c in password1):
        raise HTTPException(status_code=400, detail="password_missing_lowercase")
    if not any(c.isupper() for c in password1):
        raise HTTPException(status_code=400, detail="password_missing_uppercase")
    if not any(c.isdigit() for c in password1):
        raise HTTPException(status_code=400, detail="password_missing_digit")
    if not any(c in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/`~" for c in password1):
        raise HTTPException(status_code=400, detail="password_missing_special_character")
    
    user["password"] = password1
    return {"status_code": 200, "data": "password_changed_successfully"}

@router.put("/update_profile")
def update_profile(data: dict):
    user_id = data.get("user_id")
    profile = data.get("profile")
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")   
    
    if not profile:
        raise HTTPException(status_code=400, detail="missing_profile")
    if len(profile) > 500:
        raise HTTPException(status_code=400, detail="profile_too_long")
    
    user["profile"] = profile
    return {"status_code": 200, "data": "profile_updated_successfully"}

@router.patch("/update_username")
def update_username(data: dict):
    user_id = data.get("user_id")
    new_username = data.get("new_username")
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")   
    
    # Username validation
    if not new_username:
        raise HTTPException(status_code=400, detail="missing_username")
    if any(u["username"] == new_username for u in users):
        raise HTTPException(status_code=403, detail="username_already_exists")
    if " " in new_username:
        raise HTTPException(status_code=400, detail="username_contains_space")
    if len(new_username) > 10:
        raise HTTPException(status_code=400, detail="username_too_long")
    if new_username.lower() in {"admin", "root", "system"}:
        raise HTTPException(status_code=400, detail="username_reserved")
    
    user["username"] = new_username
    return {"status_code": 200, "data": "username_updated_successfully"}

@router.delete("/delete/{user_id}")
def delete_user(user_id: int):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")
    users.remove(user)
    return {"status_code": 200, "data": "user_deleted_successfully"}