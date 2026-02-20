from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_session
from ..models import User
from ..schemas import *
from ..auth_utils import *
from datetime import datetime, timedelta
from ..security import security
from fastapi.security import  HTTPAuthorizationCredentials


router = APIRouter()



@router.post("/signup")
async def signup(user_data: UserCreate, session: AsyncSession = Depends(get_session)):
    existing = await session.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_pwd = get_password_hash(user_data.password)
    code = generate_code()
    expires = datetime.utcnow() + timedelta(minutes=10)

    user = User(
        email=user_data.email,
        first_name=user_data.firstName,
        last_name=user_data.lastName,
        hashed_password=hashed_pwd,
        confirmation_code=code,
        confirmation_code_expires=expires
    )

    session.add(user)
    await session.commit()
    await session.refresh(user)

    print(f"Confirmation code for {user_data.email}: {code}")
    return {"message": "User created, check email for confirmation code"}


@router.post("/signin")
async def signin(credentials: Login, session: AsyncSession = Depends(get_session)):
    user = await session.execute(select(User).where(User.email == credentials.email))
    user = user.scalar_one_or_none()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    access_token = create_access_token(user.email)[0]
    refresh_token = create_refresh_token(user.email)
    auth_time = int(datetime.utcnow().timestamp())

    return {"accessToken": access_token, "refreshToken": refresh_token}

@router.post("/confirm-signup")
async def confirm_signup(data:ConfirmSignup, session: AsyncSession = Depends(get_session)):
    user = await session.execute(
        select(User).where(User.email == data.email)
    )
    
    user = user.scalar_one_or_none()

    if not user or \
       user.confirmation_code != data.confirmationCode or \
       datetime.utcnow() > user.confirmation_code_expires:
        raise HTTPException(status_code=400, detail="Invalid or expired code")
    
    user.is_verified = True
    user.confirmation_code = None
    user.confirmation_code_expires = None
    
    await session.commit()

    access_token = create_access_token(user.email)[0]
    refresh_token = create_refresh_token(user.email)

    return {
        "accessToken": access_token,
        "refreshToken": refresh_token
    }

@router.post("/resend-confirmation-code")
async def resend_confirmation(email_data: dict, session: AsyncSession = Depends(get_session)):
    user = await session.execute(
        select(User).where(
            User.email == email_data["email"],
            User.is_verified == False
        )
    )

    user = user.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found or already verified")

    code = generate_code()
    expires = datetime.utcnow() + timedelta(minutes=10)

    user.confirmation_code = code
    user.confirmation_code_expires = expires

    await session.commit()

    print(f"New code for {email_data['email']}: {code}")

    return {"message": "Code resent"}


@router.post("/forgot-password")
async def forgot_password(
    email_data: ForgotPassword, session: AsyncSession = Depends(get_session)
):

    user = await session.execute(select(User).where(User.email == email_data.email))

    user = user.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    code = generate_code()
    expires = datetime.utcnow() + timedelta(minutes=10)

    user.reset_code = code
    user.reset_code_expires = expires

    await session.commit()

    print(f"Reset code for {email_data.email}: {code}")

    return {"message": "Reset code sent to email"}


@router.post("/confirm-forgot-password")
async def confirm_forgot_password(
    data: ConfirmForgotPassword, session: AsyncSession = Depends(get_session)
):

    user = await session.execute(select(User).where(User.email == data.email))

    user = user.scalar_one_or_none()
    if not user or \
       user.reset_code != data.confirmationCode or \
       datetime.utcnow() > user.reset_code_expires:
        raise HTTPException(status_code=400, detail="Invalid or expired code")

    user.hashed_password = get_password_hash(data.newPassword)

    user.reset_code = None
    user.reset_code_expires = None

    await session.commit()

    return {"message": "Password reset successful"}


@router.post("/logout")
async def logout(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):

    return {"message": "Logged out"}


@router.get("/me")
async def get_profile(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: AsyncSession = Depends(get_session),
):
    user = await get_current_user(credentials.credentials, session)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    auth_time = int(datetime.utcnow().timestamp())
    access_token = credentials.credentials  
    user_out = user_to_out(user, access_token, auth_time)
    return {"user": user_out}

