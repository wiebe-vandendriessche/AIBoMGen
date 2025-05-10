from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import os

# This file is responsible for setting up the database connection and session management.

DATABASE_URL = os.getenv("DATABASE_URL")  # Use pymysql for synchronous MySQL

engine = create_engine(
    DATABASE_URL
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()
