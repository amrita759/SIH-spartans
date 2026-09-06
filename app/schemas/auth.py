import uuid
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRole


class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole
    organization: str
    state: str
    district: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole
    organization: str
    state: str
    district: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)