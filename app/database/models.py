from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Table, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from .db import Base, engine


# Define a User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id = Column(String, nullable=False)
    telegram_chat_id = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)

tags_association_table = Table(
    'tags_association', Base.metadata,
    Column('tip_id', Integer, ForeignKey('parenting_tips.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    tips = relationship("ParentingTip", secondary=tags_association_table, back_populates="tags", lazy=False)



# Define a ParentingTip model
class ParentingTip(Base):
    __tablename__ = 'parenting_tips'
    id = Column(Integer, primary_key=True, autoincrement=True)
    header = Column(String, nullable=False)
    tip = Column(String, nullable=False)
    age_in_days = Column(String, nullable=False)
    tags = relationship("Tag", secondary=tags_association_table, back_populates="tips", lazy=False)


# Define a ChildFriendlyPlace model
class ChildFriendlyPlace(Base):
    __tablename__ = 'child_friendly_places'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


# Create the database tables
Base.metadata.create_all(engine)
