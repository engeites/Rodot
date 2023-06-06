from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Table, ForeignKey, Boolean, Enum, Text, \
    select, func
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


class Child(Base):
    __tablename__ = 'children'
    id = Column(Integer, primary_key=True)
    # Rename age to birthdate or birthday
    age = Column(DateTime)
    sex = Column(String)
    parent_id = Column(Integer, ForeignKey('users.id'))


class ChildAdvice(Base):
    __tablename__ = 'child_advice'
    id = Column(Integer, primary_key=True)
    age_range_start = Column(Integer)
    age_range_end = Column(Integer)
    advice = Column(Text)


class Bookmark(Base):
    __tablename__ = 'bookmarks'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    bookmarked_tip_id = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    user = relationship('User', back_populates='bookmarks')


class ParentingTip(Base):
    __tablename__ = 'parenting_tips'
    id = Column(Integer, primary_key=True, autoincrement=True)
    header = Column(String, nullable=False)
    tip = Column(String, nullable=False)
    age_in_days = Column(String, nullable=False)
    category = Column(String, nullable=False)
    useful_from_day = Column(Integer)
    useful_until_day = Column(Integer)
    created_at = Column(DateTime)
    media = relationship("Media", backref="tip")
    advertisement = relationship("Advertisement", uselist=False, back_populates="parenting_tip")
    ad_logs = relationship("AdvertisementLog", back_populates="parenting_tip", cascade="all, delete-orphan")
    


class Advertisement(Base):
    __tablename__ = 'advertisements'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    image_url = Column(String)
    ad_url = Column(String)
    vendor_name = Column(String)
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime)
    tip_id = Column(Integer, ForeignKey('parenting_tips.id'), unique=True, nullable=False)
    parenting_tip = relationship("ParentingTip", back_populates="advertisement")
    logs = relationship("AdvertisementLog", back_populates="ad")

class AdvertisementLog(Base):
    __tablename__ = 'advertisement_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    ad_id = Column(Integer, ForeignKey('advertisements.id', ondelete='CASCADE'), nullable=True)
    showed_at = Column(DateTime, nullable=False)
    ad = relationship("Advertisement", back_populates="logs")
    parenting_tip_id = Column(Integer, ForeignKey('parenting_tips.id'), nullable=False)
    parenting_tip = relationship("ParentingTip", back_populates="ad_logs")

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


class AdminUser(Base):
    __tablename__ = 'admin_users'

    id = Column(Integer, primary_key=True)
    username = Column(String)


# Define the model for banned users
class BannedUser(Base):
    __tablename__ = 'banned_users'

    id = Column(Integer, primary_key=True)
    username = Column(String)


# Create the database tables
Base.metadata.create_all(engine)
