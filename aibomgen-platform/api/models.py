from sqlalchemy import Column, String
from database import Base

# This file defines the database models using SQLAlchemy ORM.


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(255), primary_key=True)  # Specify length for VARCHAR
    user_id = Column(String(255), nullable=False)  # Specify length for VARCHAR
    unique_dir = Column(String(255), nullable=False)  # Specify length for VARCHAR
    # Add other fields as necessary