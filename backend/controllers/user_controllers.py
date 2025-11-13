# controllers/user_controller.py
from fastapi import HTTPException
import bcrypt
import models.user_model as model

saltRounds = 10

def get_user(user_id: int):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="invalid_user_id")
    user = model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")
    return user

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
    if any(u["username"] == username for u in model.add_userget_users()):
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
    if any(u["email"] == email for u in model.get_users()):
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
    
    # 비밀번호 암호화
    salt = bcrypt.gensalt(rounds=saltRounds)
    hashedPassword = bcrypt.hashpw(password1.encode("utf-8"), salt).decode("utf-8")
    
    new_user = {"id": len(model.get_users()) + 1, "username": username, "email": email, "password": hashedPassword, "profile": profile}
    model.add_user(new_user)
    return new_user

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
    
    user = model.get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=401, detail="unauthorized")
    if not password:
        raise HTTPException(status_code=400, detail="missing_password")
    
    match = bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8"))
    
    if not match:
        raise HTTPException(status_code=401, detail="password does not match")

    return {"user_id": user["id"], "username": user["username"]}

def change_password(data: dict): 
    user_id = data.get("user_id")
    password1 = data.get("password1")
    password2 = data.get("password2")
    user = model.get_user_by_id(user_id)
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
    
    salt = bcrypt.gensalt(rounds=saltRounds)
    hashedPassword = bcrypt.hashpw(password1.encode("utf-8"), salt).decode("utf-8")
    user["password"] = hashedPassword

    return "password_changed_successfully"

def update_profile(data: dict):
    user_id = data.get("user_id")
    profile = data.get("profile")
    user = model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")   
    
    if not profile:
        raise HTTPException(status_code=400, detail="missing_profile")
    if len(profile) > 500:
        raise HTTPException(status_code=400, detail="profile_too_long")
    
    user["profile"] = profile
    return "profile_updated_successfully"

def update_username(data: dict):
    user_id = data.get("user_id")
    new_username = data.get("new_username")
    user = model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")   
    
    # Username validation
    if not new_username:
        raise HTTPException(status_code=400, detail="missing_username")
    if any(u["username"] == new_username for u in model.get_users()):
        raise HTTPException(status_code=403, detail="username_already_exists")
    if " " in new_username:
        raise HTTPException(status_code=400, detail="username_contains_space")
    if len(new_username) > 10:
        raise HTTPException(status_code=400, detail="username_too_long")
    if new_username.lower() in {"admin", "root", "system"}:
        raise HTTPException(status_code=400, detail="username_reserved")
    
    user["username"] = new_username
    return "username_updated_successfully"

def delete_user(user_id: int):
    user = model.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")
    delete_user(user)
    return "user_deleted_successfully"