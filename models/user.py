from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from database import Base

# Basic User Model for authentication and authorization
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    is_active = Column(Boolean, default=True)
    refresh_token = Column(String, nullable=True)