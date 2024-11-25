from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError

from email_manager import EmailManager
from db.models.user import UserCreate, UserRead, User, UserStatus
from db.models.token import Token
from db.models.confirmation_token import ConfirmationToken
from dependencies import get_session
from logger import logger
from security.hashing import verify_password, get_password_hash
from security.json_web_tokens import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201, response_model=UserRead)
def register(user: UserCreate, request: Request, session: Session = Depends(get_session)):
    user_data = user.model_dump()
    user_data["password"] = get_password_hash(user.password)

    db_user = User(**user_data)
    session.add(db_user)
    try:
        session.commit()
    except IntegrityError as e:
        session.rollback()
        error = str(e)
        if "user.username" in error:
            raise HTTPException(status_code=409, detail="Username already exists")
        
        if "user.email" in error:
            raise HTTPException(status_code=409, detail="Email already exists")

        logger.error(error)
        raise HTTPException(status_code=500, detail="Internal Server Error")

    session.refresh(db_user)
    confirmation_token = ConfirmationToken(user_id=db_user.id)
    session.add(confirmation_token)
    session.commit()
    session.refresh(confirmation_token)

    confirmation_url = f"{request.base_url}auth/confirm/{confirmation_token.token}"
    
    EmailManager.send_confirmation_link(db_user.email, confirmation_url)
    return db_user


@router.get("/confirm/{token}", name="confirm_user")
def confirm(token: str, session: Session = Depends(get_session)):
    confirmation_token = session.exec(select(ConfirmationToken).where(ConfirmationToken.token == token)).first()
    if not confirmation_token:
        raise HTTPException(status_code=404, detail="Invalid token")

    user = session.exec(select(User).where(User.id == confirmation_token.user_id)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.status = UserStatus.ACTIVE
    session.add(user)
    session.delete(confirmation_token)
    session.commit()

    return {"message": "User confirmed successfully"}


@router.post("/token")
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()], session: Session = Depends(get_session)):
    # The same exception can be raised in 2 different points
    exception = HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = session.exec(select(User).where(User.username == form.username)).first()
    if not user:
        raise exception
    
    is_password_correct = verify_password(form.password, user.password)

    if not is_password_correct:
        raise exception
    
    if user.status == UserStatus.PENDING_CONFIRMATION:
        raise HTTPException(status_code=403, detail="User must be confirmed first, please check your email")
    
    access_token = create_access_token(data={"sub": user.username})
    
    return Token(access_token=access_token, token_type="bearer")
