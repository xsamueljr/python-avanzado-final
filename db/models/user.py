from datetime import date
from enum import Enum

from sqlmodel import SQLModel, Field, Column, String
from pydantic import EmailStr, field_validator

from db.utils import generate_id


class UserStatus(Enum):
    PENDING_CONFIRMATION = "pending_confirmation"
    ACTIVE = "active"
    DISABLED = "disabled"


class UserCreate(SQLModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=16)
    name: str = Field(min_length=3, max_length=50)
    birthday: date = Field(nullable=True)

    @field_validator("birthday")
    def validate_birthday(cls, v: date):
        if v >= date.today():
            raise ValueError("Birthday must be in the past")
        return v


class User(UserCreate, table=True):
    id: str = Field(default_factory=generate_id, primary_key=True)
    email: EmailStr = Field(sa_column=Column("email", String, unique=True))
    username: str = Field(sa_column=Column("username", String, unique=True))
    joined: date = Field(default_factory=date.today, nullable=False)
    status: UserStatus = Field(default=UserStatus.PENDING_CONFIRMATION)


class UserRead(SQLModel):
    id: str
    username: str
