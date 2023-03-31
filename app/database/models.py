from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Table, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from .db import Base, engine


# Define a User model
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id = Column(String, nullable=False)
    city = Column(String)
    created_at = Column(DateTime, nullable=False)
    passed_basic_reg = Column(Boolean, default=False)
    paid = Column(Boolean, default=False)
    subscription_end = Column(DateTime)
    referral_id = Column(Integer)
    blocked_bot = Column(Boolean)
    last_seen = Column(DateTime)
    is_banned = Column(Boolean)
    children = relationship('Child', backref='parent', lazy=False)
    bookmarks = relationship('Bookmark', back_populates='user')

tags_association_table = Table(
    'tags_association', Base.metadata,
    Column('tip_id', Integer, ForeignKey('parenting_tips.id')),
    Column('tag_id', Integer, ForeignKey('tags.id'))
)

class Child(Base):
    __tablename__ = 'children'
    id = Column(Integer, primary_key=True)
    # Rename age to birthdate or birthday
    age = Column(DateTime)
    sex = Column(String)
    parent_id = Column(Integer, ForeignKey('users.id'))


class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bookmarked_tip_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    user = relationship('User', back_populates='bookmarks')

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    start_age = Column(Integer)
    end_age = Column(Integer)
    tips = relationship("ParentingTip", secondary=tags_association_table, back_populates="tags", lazy=False)



# Define a ParentingTip model
class ParentingTip(Base):
    __tablename__ = 'parenting_tips'
    id = Column(Integer, primary_key=True, autoincrement=True)
    header = Column(String, nullable=False)
    tip = Column(String, nullable=False)
    age_in_days = Column(String, nullable=False)
    useful_from_day = Column(Integer)
    useful_until_day = Column(Integer)
    created_at = Column(DateTime)
    tags = relationship("Tag", secondary=tags_association_table, back_populates="tips", lazy=False)
    media = relationship("Media", backref="tip")

class Media(Base):
    __tablename__ = 'media'
    id = Column(Integer, primary_key=True, autoincrement=True)
    media_type = Column(Enum("photo", "video", name="media_types"), nullable=False)
    media_id = Column(String, nullable=False)
    tip_id = Column(Integer, ForeignKey('parenting_tips.id'))


class DailyTip(Base):
    __tablename__ = 'daily_tips'
    id = Column(Integer, primary_key=True, autoincrement=True)
    header = Column(String, nullable=False, unique=True)
    body = Column(String, nullable=False)
    age_in_days = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    media = Column(String, nullable=True)


class BadTip(Base):
    __tablename__ = 'bad_tips'
    id = Column(Integer, primary_key=True, autoincrement=True)
    header = Column(String, nullable=False)
    tip = Column(String, nullable=False)
    age_in_days = Column(String, nullable=False)



# Define a ChildFriendlyPlace model
class ChildFriendlyPlace(Base):
    __tablename__ = 'child_friendly_places'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


class UserArticle(Base):
    __tablename__ = 'user_article'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    article_id = Column(Integer, ForeignKey('parenting_tips.id'))
    created_at = Column(DateTime, nullable=False)


# Create the database tables
Base.metadata.create_all(engine)
