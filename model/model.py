from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import sessionmaker, relationship


meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })

BASE = declarative_base(metadata=meta)

class User(BASE, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    mail = Column(String, unique=True)
    api_key = Column(String(64), unique=True)

    def __repr__(self):
        return "<User %s>" % (self.mail)


class Warehouse(BASE, SerializerMixin):
    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True)
    uuid = Column(String(32), nullable=False, unique=True)
    name = Column(String)

    def __repr__(self):
        return "<Warehouse %s>" % (self.uuid)


class Location(BASE, SerializerMixin):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    warehouse = relationship("Warehouse", back_populates="locations")

    def __repr__(self):
        return "<Location %s of warehouse %s>" % (self.id, self.warehouse_id)

Warehouse.locations = relationship("Location", order_by=Location.id, back_populates="warehouse")
