import os
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from pydantic import ValidationError
from dotenv import load_dotenv
from schemas.user_schema import TokenData
from fastapi import HTTPException

# Load environment variables
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
ACCESS_TOKEN_EXPIRE_DAYS = int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create an access token for the given data.

    Args:
        data (dict): Data to encode
        expires_delta (timedelta, optional): Custom expiration time

    Returns:
        str: Encoded JWT token

    Raises:
        JWTError: On token encoding error
        ValueError: On invalid token data
    """
    try:
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=15)

        to_encode.update({"exp": expire})

        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    except JWTError as e:
        raise JWTError(f"Failed to encode JWT token: {str(e)}")

    except ValueError as e:
        raise ValueError(f"Error creating access token: {str(e)}")


def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    """Create a refresh token for the given data.

    Args:
        data (dict): Data to encode
        expires_delta (timedelta, optional): Custom expiration time

    Returns:
        str: Encoded JWT token
    """
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except JWTError as e:
        raise JWTError(f"Failed to encode JWT token: {str(e)}")

def verify_token(token: str, credentials_exception: HTTPException) -> TokenData:
    """Verify a JWT token and return the decoded data.
    
    Args:
        token (str): The JWT token to verify
        credentials_exception (HTTPException): Exception to raise if token is invalid
    
    Returns:
        TokenData: Decoded token data
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        return TokenData(email=email)
    except (JWTError, ValidationError) as e:
        raise credentials_exception
    


