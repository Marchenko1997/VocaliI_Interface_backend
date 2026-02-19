from datetime import datetime, timedelta
from typing import Optional
import secrets
from passlib.context import CryptContext
from jose import JWTError, jwt

from .models import User
from .schemas import UserOut
import os
from sqlalchemy import select


pwd_context = CryptContext(schemes=["bcrypt_sha256"], deprecated="auto")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
SECRET_KEY = os.getenv("SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def generate_code() -> str:
    return secrets.token_hex(3).upper()  


def create_access_token(sub: str, expires_delta: Optional[timedelta] = None):
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": sub, "exp": expire, "type": "access"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, int(expire.timestamp())


def create_refresh_token(sub: str):
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": sub, "exp": expire, "type": "refresh"}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str, session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None

    user = await session.execute(select(User).where(User.email == email))
    user = user.scalar_one_or_none()
    if user and user.is_active and user.is_verified:
        return user
    return None


def user_to_out(user: User, access_token: str, auth_time: int) -> UserOut:
    issued_at = int(datetime.utcnow().timestamp())
    expires_at, _ = create_access_token(user.email)  # только для expiresAt
    expires_at = int(
        (datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp()
    )

    return UserOut(
        sub=user.id,
        email=user.email,
        name=f"{user.first_name} {user.last_name}",
        firstName=user.first_name,
        lastName=user.last_name,
        emailVerified=user.is_verified,
        userStatus="active" if user.is_active else "inactive",
        enabled=user.is_active,
        authTime=auth_time,
        issuedAt=issued_at,
        expiresAt=expires_at,
    )
