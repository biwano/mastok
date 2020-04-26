from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import sessionmaker, relationship, backref


meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })

BASE = declarative_base(metadata=meta)
def ManyToOne(remote_table, remote_field):
    return relationship(remote_table,
                        backref=backref(remote_field, single_parent=True),
                        cascade="save-update, merge, delete, delete-orphan")

class User(BASE, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    mail = Column(String, unique=True)
    api_key = Column(String(32), unique=True)
    warehouse_aces = ManyToOne("Warehouse_ACE", "user")

    serialize_rules = ('-warehouse_aces',)

    def __repr__(self):
        return "<User %s>" % (self.mail)


class Warehouse(BASE, SerializerMixin):
    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    aces = ManyToOne("Warehouse_ACE", "warehouse")
    locations = ManyToOne("Location", "warehouse")

    serialize_rules = ('-aces.warehouse', '-locations',)

    def __repr__(self):
        return "<Warehouse %s: %s>" % (self.id, self.name)


class Location(BASE, SerializerMixin):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))

    def __repr__(self):
        return "<Location %s of warehouse %s>" % (self.id, self.warehouse_id)


class Warehouse_ACE(BASE, SerializerMixin):
    __tablename__ = 'warehouse_aces'

    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role = Column(String(20))

    def __repr__(self):
        return "<User %s is %s of Warehouse %s>" % (self.user_id, self.role, self.warehouse_id)
