from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    created_at: datetime


class PasswordChange(BaseModel):
    old_password: str
    new_password: str
    new_password_confirmation: str
