from sqlalchemy import Column, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
from sqlalchemy.types import Integer, Float, Text, DateTime, ARRAY, JSON

from scrapy.utils.project import get_project_settings


DeclarativeBase = declarative_base()

def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(get_project_settings().get("CONNECTION_STRING"))

class Injuries(DeclarativeBase):
    """Sqlalchemy lines model"""
    __tablename__ = "injuries"

    week_key = Column(Text, primary_key=True)
    player_key = Column(Text, primary_key=True)
    position = Column(Text)
    injury_location = Column(Text)
    participation = Column(Text)
