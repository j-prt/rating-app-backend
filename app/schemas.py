"""Pydantic models for ratings app."""

from pydantic import BaseModel
import datetime


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


class RatingItemBase(BaseModel):
    category: str
    title: str

    image: str | None = None
    address: str | None = None
    latitude: int | None = None
    longitude: int | None = None

    class Config:
        orm_mode = True


class RatingItem(RatingItemBase):
    id: int
    userId: int
    time_created: datetime.datetime
    time_updated: datetime.date | None = None


class RatingBase(BaseModel):
    rating: int
    itemId: int
    description: str | None = None


class Rating(RatingBase):
    id: int
    userId: int
    title: str

    class Config:
        orm_mode = True


class RatingSuccess(RatingBase):
    id: int
    userId: int

    class Config:
        orm_mode = True


class CreateRatingItem(RatingItemBase):
    rating: int
    description: str | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None
