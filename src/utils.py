from sqlalchemy.orm import Session
from passlib.context import CryptContext

from models import User

# openssl rand -hex 32
SECRET_KEY = "6b1b65befcf7c4fcaedd3204722f52a33aa8d9980a985146b455555337dda0a2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_password_hash(password):
    return pwd_context.hash(password)


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)
