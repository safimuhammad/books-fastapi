from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv
from sqlalchemy.pool import StaticPool

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
from sqlalchemy.pool import StaticPool

# Update your create_engine call to include:
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()