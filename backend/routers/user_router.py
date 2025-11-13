# routers/user_router.py
from fastapi import APIRouter
from controllers import user_controllers as controller

router = APIRouter(prefix="/users")

@router.get("/{user_id}")
async def get_user(user_id: int):
    return controller.get_user(user_id)

@router.post("/register", status_code=201)
async def create_user(data: dict):
    return controller.create_user(data)

@router.post("/login")
async def login(data: dict):
    return controller.login(data)

@router.patch("/change_password")
async def change_password(data: dict): 
    return change_password(data)

@router.put("/update_profile")
async def update_profile(data: dict):
    return update_profile(data)

@router.patch("/update_username")
async def update_username(data: dict):
    return update_username(data)

@router.delete("/delete/{user_id}")
async def delete_user(user_id: int):
    return delete_user(user_id)