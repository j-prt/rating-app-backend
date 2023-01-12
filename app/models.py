"""Database models for ratings app."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship  # noqa

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String)
    last_name = Column(String)
    password_hash = Column(String)

#    items = relationship("Item", back_populates="owner")
