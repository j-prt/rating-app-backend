"""Database models for ratings app."""

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Float,
    DateTime,
    CheckConstraint,
    UniqueConstraint
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship  # noqa

from .db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    password_hash = Column(String)


class RatingItem(Base):
    __tablename__ = 'rating_items'

    id = Column(Integer, primary_key=True, index=True)
    userId = Column(ForeignKey('users.id'))
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    image = Column(String)
    address = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    check = CheckConstraint(
        '''
        (latitude IS NOT NULL AND longitude IS NOT NULL)
        OR (latitude IS NULL AND longitude IS NULL)
        ''')


class Rating(Base):
    __tablename__ = 'ratings'

    id = Column(Integer, primary_key=True, index=True)
    itemId = Column(ForeignKey('rating_items.id'), nullable=False)
    userId = Column(ForeignKey('users.id'), nullable=False)
    rating = Column(Integer, nullable=False)
    description = Column(String)

    unique_user_item = UniqueConstraint('itemId', 'userId')
