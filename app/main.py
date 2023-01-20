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


@app.post('/ratings', response_model=schemas.Rating, status_code=201)
def post_rating(data: schemas.RatingBase | schemas.CreateRatingItem,
                db: Session = Depends(get_db),
                user: models.User = Depends(auth_required)):
    print(data)
    if isinstance(data, schemas.RatingBase):
        data = data.dict()
        rating = crud.create_rating(db, user.id, data)

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
        rating_item = crud.create_rating_item(db, user.id, data)

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
        rating = crud.create_rating(db, user.id, rating_data)
        return rating
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='No good. Try again, but right this time.',
        )


@app.get('/ratings', response_model=list[schemas.Rating])
def get_ratings(db: Session = Depends(get_db),
                user: models.User = Depends(auth_required)):
    results = crud.get_user_ratings(db, user.id)
    print(results)
    return results


@app.get('/item/{item_id}', response_model=schemas.RatingItem)
def get_item_detail(item_id: int,
                    db: Session = Depends(get_db),
                    user: models.User = Depends(auth_required)):
    return crud.get_rating_item(db, item_id)
