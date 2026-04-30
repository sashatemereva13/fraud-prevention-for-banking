from fastapi import APIRouter

from app.models.user_schema import UserCreate
from app.services.user_service import (
    create_user,
    get_all_users,
    get_user_by_id
)

router = APIRouter()

# CREATE USER
@router.post("/users")
def add_user(user: UserCreate):
    return create_user(user.model_dump())

# GET ALL USERS
@router.get("/users")
def fetch_users():
    return get_all_users()

# GET USER BY ID
@router.get("/users/{user_id}")
def fetch_user(user_id: str):
    return get_user_by_id(user_id)