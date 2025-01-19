from sqlalchemy import Column, Integer, String, Boolean,Date
from database import Base
from datetime import datetime, timezone

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    author = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    genre = Column(String, nullable=True)
    published_date = Column(Date, nullable=True) 