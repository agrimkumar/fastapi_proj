from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from starlette import status

from database import SessionLocal
from models import User
from utils import get_user_by_email, get_password_hash

router = APIRouter(
    prefix='/api/v1',
    tags=['user']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class UserBase(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True


@router.get('/users', response_model=list[UserOut])
def read_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(User).offset(skip).limit(limit).all()


@router.get('/users/{user_id}', response_model=UserOut)
def read_user(user_id: int = Path(gt=0), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User does not exists!")
    return user


@router.post('/users', response_model=UserOut)
def create_user(user_request: UserCreate, db: Session = Depends(get_db)):
    is_user_exists = get_user_by_email(db, email=user_request.email)
    if is_user_exists:
        raise HTTPException(status_code=400, detail="Email Already Exists!")
    user = User(
        firstname=user_request.firstname,
        lastname=user_request.lastname,
        email=user_request.email,
        password=get_password_hash(user_request.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.put('/users/{user_id}', response_model=UserOut)
def update_user(user_request: UserBase, user_id: int = Path(gt=0), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User does not exists!")
    user.firstname = user_request.firstname
    user.lastname = user_request.lastname
    user.email = user_request.email
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.delete('/users/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int = Path(gt=0), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User does not exists!")
    db.query(User).filter(User.id == user_id).delete()
    db.commit()
