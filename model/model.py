from sqlalchemy import create_engine, Column, String, Integer, TIMESTAMP, DATE, Table, ForeignKey, MetaData, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import sessionmaker, relationship, backref
import datetime


meta = MetaData(naming_convention={
        "ix": "ix_%(column_0_label)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s"
      })

BASE = declarative_base(metadata=meta)
BASE.modified = Column(TIMESTAMP, default=datetime.datetime.now, onupdate=datetime.datetime.now)

def ManyToOne(remote_table, remote_field):
    return relationship(remote_table,
                        backref=backref(remote_field, single_parent=True),
                        cascade="save-update, merge, delete, delete-orphan")

class User(BASE, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    mail = Column(String, unique=True, nullable=False)
    api_key = Column(String(32), unique=True)
    warehouse_aces = ManyToOne("Warehouse_ACE", "user")

    serialize_rules = ('-warehouse_aces',)

    def __repr__(self):
        return "<User %s: %s>" % (self.id, self.mail)


class Warehouse(BASE, SerializerMixin):
    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    aces = ManyToOne("Warehouse_ACE", "warehouse")
    locations = ManyToOne("Location", "warehouse")
    references = ManyToOne("Reference", "warehouse")
    categories = ManyToOne("Category", "warehouse")

    serialize_rules = ('-aces', '-locations.warehouse', '-references.warehouse', '-categories.warehouse')

    def __repr__(self):
        return "<Warehouse %s: %s>" % (self.id, self.name)


class Location(BASE, SerializerMixin):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))

    items = ManyToOne("Item", "location")

    serialize_rules = ('-warehouse', )
    UniqueConstraint('warehouse_id', 'name', name='uniq_location_name')

    def __repr__(self):
        return "<Location %s of warehouse %s: %s>" % (self.id, self.warehouse_id, self.name)


class Warehouse_ACE(BASE, SerializerMixin):
    __tablename__ = 'warehouse_aces'

    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role = Column(String(20), nullable=False)

    def __repr__(self):
        return "<User %s is %s of Warehouse %s: %s>" % (self.user_id, self.role, self.warehouse_id, self.name)

ReferenceCategory = Table('ReferenceCategory', BASE.metadata,
    Column('reference_id', Integer, ForeignKey('references.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True))

class Reference(BASE, SerializerMixin):
    __tablename__ = 'references'

    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    name = Column(String, nullable=False)
    items = ManyToOne("Item", "reference")
    categories = relationship("Category", secondary=ReferenceCategory, backref="references")
    target_quantity = Column(Integer)
    UniqueConstraint('warehouse_id', 'name', name='uniq_reference_name')

    serialize_only = ('id', 'warehouse_id', 'name', 'target_quantity', 'categories.name', 'categories.id')

    def __repr__(self):
        return "<Reference %s of Warehouse %s: %s>" % (self.id, self.warehouse_id, self.name)

class Category(BASE, SerializerMixin):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    name = Column(String, nullable=False)
    #references = relationship("Reference", secondary=ReferenceCategory, backref="categories")
    UniqueConstraint('warehouse_id', 'name', name='uniq_category_name')

    serialize_only = ('id', 'warehouse_id', 'name', 'references.name', 'references.id')

    def __repr__(self):
        return "<Category %s of Warehouse %s: %s>" % (self.id, self.warehouse_id, self.name)




class Item(BASE, SerializerMixin):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    reference_id = Column(Integer, ForeignKey('references.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    quantity = Column(Integer, nullable=False)
    expiry  = Column(DATE)

    serialize_rules = ('-location', 'reference.name', '-reference.warehouse', '-reference.items')

    def __repr__(self):
        return "<Item %s in location %s>" % (self.reference_id, self.location_id)

