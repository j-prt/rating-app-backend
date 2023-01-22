"""Utility functions for effecting CRUD operations in ratings app."""

from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from . import models, schemas, auth


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> models.User | None:
    return db.query(models.User).filter(
        models.User.email.ilike(email)
    ).first()


def get_user_by_username(db: Session, username: str) -> models.User | None:
    return db.query(models.User).filter(
        models.User.username.ilike(username)
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


def create_rating_item(db: Session,
                       user_id: int,
                       data: dict) -> models.RatingItem | None:
    try:
        rating_item = models.RatingItem(
            userId=user_id,
            **data,
        )
        db.add(rating_item)
        db.commit()
    except IntegrityError:
        return None
    db.refresh(rating_item)
    return rating_item


def create_rating(db: Session,
                  user_id: int,
                  data: dict) -> models.Rating | None:
    try:
        rating = models.Rating(
            userId=user_id,
            **data,
        )
        db.add(rating)
        db.commit()
    except IntegrityError:
        return None
    db.refresh(rating)
    return rating


def delete_rating(db: Session, user_id, rating_id) -> bool:
    rating = db.query(models.Rating).filter(
        models.Rating.id == rating_id
    ).first()

    if not rating:
        return False
    elif rating.userId != user_id:
        return False
    else:
        db.delete(rating)
        db.commit()
        return True


def get_user_ratings(db: Session, user_id: int) -> schemas.Rating:
    query = select(
        models.Rating,
        models.RatingItem.title
        ).join(
            models.Rating.itemId,
            models.Rating.itemId == models.RatingItem.id
        ).where(
            models.Rating.userId == user_id
        )
    result = db.execute(query).all()

    # This line takes the joined query results and converts the
    # row tuples into a new dictionary adding the key of 'title'
    results_list = [{**x[0].__dict__, 'title': x[1]} for x in result]
    return results_list


def get_rating_item(db: Session, item_id: int):
    return db.query(models.RatingItem).filter(
        models.RatingItem.id == item_id
    ).first()


def delete_rating_item(db: Session, user_id, item_id) -> bool:
    item = db.query(models.RatingItem).filter(
        models.RatingItem.id == item_id
    ).first()
    if not item:
        return False
    elif item.userId != user_id:
        return False
    else:
        ratings = db.query(models.Rating).filter(
            models.Rating.itemId == item.id
        ).all()
        if len(ratings) > 1:
            return False
        elif ratings and ratings[0].userId != user_id:
            return False
        else:
            db.delete(item)
            db.commit()
            return True
