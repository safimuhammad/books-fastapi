import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from auth.jwt import verify_token
from database import engine, Base
from models.user import User
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
from deps import limiter, get_db

load_dotenv()
Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Books API",
    description="RESTful API for book management with user authentication, featuring CRUD operations and real-time updates",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc", # Added for future use in case of new documentation page
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(
    SessionMiddleware, secret_key=os.getenv("SECRET_KEY"), https_only=True
)
api_version = os.getenv("API_VERSION")
# Rate limiting for all routes to prevent abuse
app.state.limiter = limiter
app.add_exception_handler(429, _rate_limit_exceeded_handler)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{api_version}/auth/login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
):
    """Get the current user from the database."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = verify_token(token, credentials_exception)
    user = db.query(User).filter(User.email == token_data.email).first()
    if not user:
        raise credentials_exception
    return user


from routers.auth_api import router as auth_router
from routers.books_api import router as books_router

app.include_router(auth_router, prefix=f"/{api_version}/auth")
app.include_router(books_router, prefix=f"/{api_version}/books")
