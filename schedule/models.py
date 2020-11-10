from sqlalchemy import Column, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.types import Integer, DateTime, Text
import os

from connection_str import *


DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(CONNECTION_STRING)

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(CONNECTION_STRING)

class Weeks(DeclarativeBase):
    """Sqlalchemy lines model"""
    __tablename__ = "weeks"

    week = Column(Integer)
    season = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    week_key = Column(Text, primary_key=True)
    season_part = Column(Text)