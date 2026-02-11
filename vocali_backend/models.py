from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase



class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    confirmation_code = Column(String, nullable=True)
    confirmation_code_expires = Column(DateTime, nullable=True)
    reset_code = Column(String, nullable=True)
    reset_code_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
