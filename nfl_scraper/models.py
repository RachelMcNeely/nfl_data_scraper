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

class InjuryReport(DeclarativeBase):
    """Sqlalchemy lines model"""
    __tablename__ = "injury_report"

    year = Column(Integer)
    week = Column(Integer)
    team_key = Column(Text)
    week_key = Column(Text)
    player_key = Column(Text)
    position = Column(Text)
    injury_location = Column(Text)
    game_status = Column(Text)
    injury_key = Column(Text, primary_key=True)  ## team_key + week_key + player_key + (report | reserve)

# class Injuries(DeclarativeBase):
#     """Sqlalchemy lines model"""
#     __tablename__ = "injuries"

#     team_key = Column(Text, primary_key=True)
#     week_key = Column(Text, primary_key=True)
#     player_key = Column(Text, primary_key=True)
#     position = Column(Text)
#     injury_location = Column(Text)
#     participation = Column(Text)


class InjuryReserve(DeclarativeBase):
    """Sqlalchemy lines model"""
    __tablename__ = "injury_reserve"

    injury_key = Column(Text, primary_key=True)
    team = Column(Text)
    year = Column(Integer)
    month = Column(Integer)
    player_key = Column(Text)
    date = Column(DateTime)
    position = Column(Text)
    transaction = Column(Text)
