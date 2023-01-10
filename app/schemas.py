"""Pydantic models for ratings app."""

from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserValidate(UserBase):
    password: str

class UserCreate(UserBase):
    password: str
    username: str
    first_name: str | None = None
    last_name: str | None = None


class User(UserBase):
    id: int
    username: str
    first_name: str | None = None
    last_name: str | None = None

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
