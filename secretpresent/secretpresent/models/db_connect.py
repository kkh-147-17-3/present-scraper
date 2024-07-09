import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")

engine = create_engine(f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_DATABASE}")

session_local = sessionmaker(autocommit=False, bind=engine)