import traceback
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from config import config
from .model import BASE, User, Warehouse, Location

ENGINE = create_engine(config.get("sqlalchemy", "url"), echo=True)
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


#BASE.metadata.create_all(ENGINE)
