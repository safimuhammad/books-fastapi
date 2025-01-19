from auth.jwt import create_access_token, create_refresh_token, verify_token
from auth.utils import hash_password, verify_password
from schemas.user_schema import UserCreate, UserOut, Token
from models.user import User
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from sqlalchemy.orm import Session
from deps import get_db, limiter
from fastapi.security import OAuth2PasswordRequestForm
import os
from fastapi.responses import JSONResponse

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserOut)
@limiter.limit("5/minute")  # Rate limiting: 5 requests per minute per IP
async def register(
    request: Request,
    user: UserCreate,
    db: Session = Depends(get_db),
):
    """Registers a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    try:
        # Create new user
        hashed_password = hash_password(user.password)
        db_user = User(email=user.email, hashed_password=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error registering user: {str(e)}",
        )


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Rate limiting: 5 requests per minute per IP
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Logs in a user."""
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        if not verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        access_token = create_access_token(data={"sub": user.email})
        refresh_token = create_refresh_token(data={"sub": user.email})
        user.refresh_token = refresh_token
        db.commit()
        db.refresh(user)
        response_data = {"access_token": access_token, "token_type": "bearer"}
        response = JSONResponse(content=response_data)
        max_age = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS")) * 24 * 60 * 60
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="strict",
            max_age=max_age,
        )
        return response

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}",
        )


@router.get("/logout")
@limiter.limit("5/minute")  # Rate limiting: 5 requests per minute per IP
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Logs out the user by invalidating the refresh token stored in cookies.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token missing")

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(refresh_token, credential_exception)
    user = db.query(User).filter(User.email == token_data.email).first()

    if user is None or user.refresh_token != refresh_token:
        raise credential_exception

    # Invalidate the refresh token
    user.refresh_token = None
    db.commit()
    response.delete_cookie(key="refresh_token")

    return {"message": "Successfully logged out."}
