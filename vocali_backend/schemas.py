from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)
    firstName: str
    lastName: str


class UserOut(BaseModel):
    sub: Optional[int] = None
    email: str
    name: str
    firstName: str
    lastName: str
    username: Optional[str] = None  
    emailVerified: bool
    userStatus: str = "active"
    enabled: bool
    tokenUse: str = "auth"
    scope: str = "user"
    authTime: int = Field(..., description="timestamp")
    issuedAt: int = Field(..., description="timestamp")
    expiresAt: int = Field(..., description="timestamp")


class Token(BaseModel):
    accessToken: str
    refreshToken: str


class ConfirmSignup(BaseModel):
    email: EmailStr
    confirmationCode: str = Field(min_length=6, max_length=6)


class ForgotPassword(BaseModel):
    email: EmailStr


class ConfirmForgotPassword(BaseModel):
    email: EmailStr
    confirmationCode: str = Field(min_length=6, max_length=6)
    newPassword: str = Field(min_length=8)


class Login(BaseModel):
    email: EmailStr
    password: str
