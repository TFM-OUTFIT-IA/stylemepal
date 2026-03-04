from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from .schemas import UserCreate
from ..db.database import get_db
from ..db.models import UserDB
from ..core.security import get_password_hash, verify_password, create_access_token
from src.api.schemas import UserCreate, GenericMessageResponse, Token

logger = logging.getLogger(__name__)


auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_router.post("/register", response_model=GenericMessageResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)) -> GenericMessageResponse:
    try:
        logger.info("Attempting to register user: %s, with password %d", user.username, user.password)
        # Check for existing user
        if db.query(UserDB).filter(UserDB.username == user.username).first():
            raise HTTPException(status_code=400, detail="Username already registered")

        new_user = UserDB(username=user.username, hashed_password=get_password_hash(user.password))
        db.add(new_user)
        db.commit()
        return GenericMessageResponse(message="User created successfully")
        
    except IntegrityError:
        db.rollback()
        logger.exception("Integrity error during registration: duplicate username.")
        raise HTTPException(status_code=400, detail="Username already registered")
        
    except SQLAlchemyError as db_err:
        db.rollback()
        logger.exception("Database error during user registration: %s", db_err)
        raise HTTPException(status_code=500, detail="Database error while creating user")

@auth_router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    try:
        user = db.query(UserDB).filter(UserDB.username == form_data.username).first()
    except SQLAlchemyError:
        logger.exception("Database error during login for %s", form_data.username)
        raise HTTPException(status_code=500, detail="Database error")

    if not user or not verify_password(form_data.password, user.hashed_password):
        # Must return 401 with WWW-Authenticate header per standard
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")