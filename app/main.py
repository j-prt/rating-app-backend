"""Routes and logic for ratings app back end API."""

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import crud, models, schemas, auth
from .db import SessionLocal, engine


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def auth_required(db: Session = Depends(get_db),
                  email: str = Depends(auth.get_current_user)):
    auth_user = crud.get_user_by_email(db, email=email)
    return auth_user


@app.get('/status')
def check_status(db: Session = Depends(get_db),
                 user: models.User = Depends(auth_required)):
    return JSONResponse(status_code=200, content={'message': 'Auth Confirmed'})


@app.post('/users', response_model=schemas.User, status_code=201)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_email = crud.get_user_by_email(db, email=user.email)
    if db_email:
        raise HTTPException(status_code=400, detail='Email already in use.')
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail='Username already in use.')
    return crud.create_user(db=db, user=user)


@app.get('/users', response_model=list[schemas.User])
def read_users(db: Session = Depends(get_db),
               user: models.User = Depends(auth_required)):
    users = crud.get_users(db)
    return users


@app.get('/users/{user_id}', response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    return db_user


@app.post('/token')
def login(user: schemas.UserValidate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email or password incorrect',
            headers={"WWW-Authenticate": "Bearer"},
        )
    auth_user = auth.authenticate_user(user, db_user.password_hash)
    if not auth_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Email or password incorrect',
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = auth.create_access_token(
        data={"sub": db_user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post('/ratings')
def post_rating(data: schemas.RatingBase | schemas.CreateRatingItem,
                db: Session = Depends(get_db)):
    print(data)
    if isinstance(data, schemas.RatingBase):
        data = data.dict()
        rating = crud.create_rating(db, 1, data)
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User already has a rating for this item.'
            )
        return rating
    elif isinstance(data, schemas.CreateRatingItem):
        data = data.dict()
        rating = data.pop('rating')
        desc = data.pop('description', None)

        rating_item = crud.create_rating_item(db, 1, data)
        if not rating_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Incomplete latitude and longitude provided.'
            )
        rating_data = {
            'rating': rating,
            'itemId': rating_item.id
        }
        if desc:
            rating_data['description'] = desc
        rating = crud.create_rating(db, 1, rating_data)
        return rating
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No good. Try again, but right this time.',
        )
    # Should be able to submit either a rating
    # or a rating + the description of an item,
    # which will then be created.
    # So the logic for case a) :
    # User submits json with rating data and item id,
    # rating is simply submitted.
    # Logic for case b):
    # User submits json with both rating data and item
    # information -> item data is used to create item in db
    # then rating is created linked to the new item

    # Don't forget to test the lat/long constraint!
    pass


@app.get('/ratings')
def get_ratings():
    pass


@app.get('/ratings/{item_id}')
def get_rating_detail(item_id: int):
    pass
