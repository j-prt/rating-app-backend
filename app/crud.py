"""Utility functions for effecting CRUD operations in ratings app."""

from sqlalchemy.orm import Session

from . import models, schemas, auth


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(
        models.User.email == email
    ).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(
        models.User.username == username
    ).first()


def get_users(db: Session) -> list:
    return db.query(models.User).all()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    hashed_password = auth.hash_password(user.password)
    db_user = models.User(
        email=user.email,
        password_hash=hashed_password,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
