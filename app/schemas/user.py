from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    id: str
    username: str


class UserResponse(UserCreate):
    user_id: str
    pass
