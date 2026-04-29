from pydantic import BaseModel, EmailStr
from datetime import datetime


# USER CREATE 
class UserCreate(BaseModel):
    user_id: str
    name: str
    email: EmailStr


# USER RESPONSE 
class UserResponse(BaseModel):
    user_id: str
    name: str
    email: EmailStr
    created_at: datetime