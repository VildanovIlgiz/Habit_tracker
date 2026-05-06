from __future__ import annotations
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config import get_settings


class Base(DeclarativeBase):
    pass


settings = get_settings()

engine = create_engine(settings.database_url, echo=settings.debug)

SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    from database import models  

    Base.metadata.create_all(bind=engine)