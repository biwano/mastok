from contextlib import contextmanager
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config
from sqlalchemy_serializer import SerializerMixin

ENGINE = create_engine(config.get("sqlalchemy", "url"), echo=True)
SESSION = sessionmaker(bind=ENGINE)
BASE = declarative_base()


@contextmanager
def Session():
    try:
        session = SESSION()
        yield session
        session.commit()
    except:
        session.rollback()
    finally:
        session.close()


class Warehouse(BASE, SerializerMixin):
    __tablename__ = 'warehouses'

    uuid = Column(String(32), primary_key=True)

    def __repr__(self):
        return "<Warehouse %s>" % (self.uuid)
