import traceback
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
import config
from .model import BASE, User, Warehouse, Warehouse_ACE, Location, Reference, Category, Item
from . import queries

ENGINE = create_engine(config.get("sqlalchemy", "url"), 
                       echo=config.getboolean("sqlalchemy", "echo"))
SESSION = sessionmaker(bind=ENGINE)


@contextmanager
def Session():
    try:
        session = SESSION()
        yield session
        session.commit()
    except Exception:
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

