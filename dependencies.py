from typing import Annotated
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select

from db.config import engine
from db.models.user import User, UserStatus
from security.json_web_tokens import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_session():
    with Session(engine) as session:
        yield session


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Session = Depends(get_session)) -> User:
    exception = HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    username = decode_access_token(token)
    if username is None:
        raise exception
    
    user = session.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise exception
    
    return user
