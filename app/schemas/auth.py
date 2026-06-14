from pydantic import BaseModel


class RegisterRequest(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class RegisterResponse(BaseModel):
    id: int
    username: str

class UserResponse(BaseModel):
    id: int
    username: str
    is_active: bool
    is_admin: bool