from sqlalchemy import create_engine, Column, String, Integer, TIMESTAMP, DATE, Table, ForeignKey, MetaData, UniqueConstraint, Boolean
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
BASE.created = Column(TIMESTAMP, default=datetime.datetime.now)
BASE.modified = Column(TIMESTAMP, default=datetime.datetime.now, onupdate=datetime.datetime.now)

def ManyToOne(remote_table, remote_field, delete_cascade=False):
    if delete_cascade:
        cascade = "all, delete-orphan"
    else:
        cascade = "save-update, merge"
    return relationship(remote_table,
                        backref=backref(remote_field, single_parent=True),
                        cascade=cascade)


class User(BASE, SerializerMixin):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    mail = Column(String, nullable=False)
    passcode = Column(String(8), nullable=True)
    is_mail_verified = Column(Boolean(create_constraint=False))
    warehouse_aces = ManyToOne("WarehouseACE", "user", delete_cascade=True)
    api_keys = ManyToOne("ApiKey", "user", delete_cascade=True)

    serialize_only = ('id', 'mail', 'is_mail_verified')

    UniqueConstraint('mail', name='uniq_user_mail')

    def __repr__(self):
        return "<User %s: %s>" % (self.id, self.mail)

class ApiKey(BASE, SerializerMixin):
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    api_key = Column(String(32), nullable=True)    


class Warehouse(BASE, SerializerMixin):
    __tablename__ = 'warehouses'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    aces = ManyToOne("WarehouseACE", "warehouse", delete_cascade=True)
    locations = ManyToOne("Location", "warehouse", delete_cascade=True)
    references = ManyToOne("Reference", "warehouse", delete_cascade=True)
    categories = ManyToOne("Category", "warehouse", delete_cascade=True)
    tags = ManyToOne("Tag", "warehouse", delete_cascade=True)
    articles = ManyToOne("Article", "warehouse", delete_cascade=True)

    serialize_only = ('id', 'name')

    def __repr__(self):
        return "<Warehouse %s: %s>" % (self.id, self.name)


class Location(BASE, SerializerMixin):
    __tablename__ = 'locations'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))

    articles = ManyToOne("Article", "location")

    serialize_only = ('id', 'name', 'warehouse_id')
    UniqueConstraint('warehouse_id', 'name', name='uniq_location_name')

    def __repr__(self):
        return "<Location %s of warehouse %s: %s>" % (self.id, self.warehouse_id, self.name)


class WarehouseACE(BASE, SerializerMixin):
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
    articles = ManyToOne("Article", "reference", delete_cascade=True)
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


ArticleTag = Table('ArticleTag', BASE.metadata,
    Column('article_id', Integer, ForeignKey('articles.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True))

class Article(BASE, SerializerMixin):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'), nullable=False)
    reference_id = Column(Integer, ForeignKey('references.id'))
    location_id = Column(Integer, ForeignKey('locations.id'))
    quantity = Column(Integer, nullable=False)
    expiry = Column(DATE)
    tags = relationship("Tag", secondary=ArticleTag, backref="articles")

    serialize_only = ('id', 'warehouse_id', 'reference_id', 'location_id', 'quantity', 'expiry',
        'reference.name', 'location.name', 'warehouse.name', 'tags.id', 'tags.warehouse_id', 'tags.name')

    def __repr__(self):
        return "<Article %s in location %s>" % (self.reference_id, self.location_id)

class Tag(BASE, SerializerMixin):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True)
    warehouse_id = Column(Integer, ForeignKey('warehouses.id'))
    name = Column(String, nullable=False)
    UniqueConstraint('warehouse_id', 'name', name='uniq_category_name')

    serialize_only = ('id', 'warehouse_id', 'name')

    def __repr__(self):
        return "<Tag %s of Warehouse %s: %s>" % (self.id, self.warehouse_id, self.name)