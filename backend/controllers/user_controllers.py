# controllers/user_controller.py
from fastapi import HTTPException
from sqlalchemy.orm import Session
import bcrypt
import models.user_model as model

saltRounds = 10


def get_user(db: Session, user_id: int):
    if user_id <= 0:
        raise HTTPException(status_code=400, detail="invalid_user_id")

    user = model.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")

    return user


def create_user(db: Session, data: dict):
    username = data.get("username")
    email = data.get("email")
    password1 = data.get("password1")
    password2 = data.get("password2")
    profile = data.get("profile")

    # -------- Profile validation --------
    if not profile:
        raise HTTPException(status_code=400, detail="missing_profile")
    if profile and len(profile) > 500:
        raise HTTPException(status_code=400, detail="profile_too_long")

    # -------- Username validation --------
    if not username:
        raise HTTPException(status_code=400, detail="missing_username")
    if " " in username:
        raise HTTPException(status_code=400, detail="username_contains_space")
    if len(username) > 10:
        raise HTTPException(status_code=400, detail="username_too_long")
    if username.lower() in {"admin", "root", "system"}:
        raise HTTPException(status_code=400, detail="username_reserved")

    # DB 중복 체크
    if model.get_user_by_username(db, username):
        raise HTTPException(status_code=403, detail="username_already_exists")

    # -------- Password validation --------
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

    # -------- Email validation --------
    if not email:
        raise HTTPException(status_code=400, detail="missing_email")

    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="invalid_email_format")
    if len(email) > 254:
        raise HTTPException(status_code=400, detail="email_too_long")
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

    # DB 중복 이메일 체크
    if model.get_user_by_email(db, email):
        raise HTTPException(status_code=403, detail="email_already_exists")

    # -------- 실제 사용자 생성 (모델 함수 사용) --------
    new_user = model.create_user(
        db=db,
        username=username,
        email=email,
        raw_password=password1,  # 여기서는 RAW 패스워드 전달 → model에서 해시
        profile=profile,
    )
    return new_user


def login(db: Session, data: dict):
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

    user = model.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=401, detail="unauthorized")

    if not password:
        raise HTTPException(status_code=400, detail="missing_password")

    # user.password 는 이미 해시된 값 (str)
    match = bcrypt.checkpw(password.encode("utf-8"), user.password.encode("utf-8"))
    if not match:
        raise HTTPException(status_code=401, detail="password_does_not_match")

    return {"user_id": user.id, "username": user.username}


def change_password(db: Session, data: dict):
    user_id = data.get("user_id")
    password1 = data.get("password1")
    password2 = data.get("password2")

    user = model.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")

    # -------- Password validation (동일 로직 재사용) --------
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

    # 새 비밀번호 해시 후 저장
    hashed_password = model.hash_pw(password1)
    user.password = hashed_password
    db.commit()
    db.refresh(user)

    return {"status_code": 200, "detail": "password_changed_successfully"}


def update_profile(db: Session, data: dict):
    user_id = data.get("user_id")
    profile = data.get("profile")

    user = model.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")

    if not profile:
        raise HTTPException(status_code=400, detail="missing_profile")
    if len(profile) > 500:
        raise HTTPException(status_code=400, detail="profile_too_long")

    updated_user = model.update_user(db, user_id=user_id, profile=profile)
    if not updated_user:
        raise HTTPException(status_code=500, detail="failed_to_update_profile")

    return {"status_code": 200, "detail": "profile_updated_successfully"}


def update_username(db: Session, data: dict):
    user_id = data.get("user_id")
    new_username = data.get("new_username")

    user = model.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")

    # Username validation
    if not new_username:
        raise HTTPException(status_code=400, detail="missing_username")
    if " " in new_username:
        raise HTTPException(status_code=400, detail="username_contains_space")
    if len(new_username) > 10:
        raise HTTPException(status_code=400, detail="username_too_long")
    if new_username.lower() in {"admin", "root", "system"}:
        raise HTTPException(status_code=400, detail="username_reserved")

    # 중복 체크
    exist = model.get_user_by_username(db, new_username)
    if exist and exist.id != user_id:
        raise HTTPException(status_code=403, detail="username_already_exists")

    updated_user = model.update_user(db, user_id=user_id, username=new_username)
    if not updated_user:
        raise HTTPException(status_code=500, detail="failed_to_update_username")

    return {"status_code": 200, "detail": "username_updated_successfully"}


def delete_user(db: Session, user_id: int):
    user = model.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="user_not_found")

    success = model.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=500, detail="failed_to_delete_user")

    return {"status_code": 200, "detail": "user_deleted_successfully"}
