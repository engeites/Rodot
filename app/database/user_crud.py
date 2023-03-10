from datetime import datetime

from sqlalchemy.orm import sessionmaker
from typing import List, Type
from .models import User, Child, Bookmark
from .db import engine

from app.utils.validators import calculate_age_in_days


Session = sessionmaker(bind=engine)


def get_user_by_id(user_id: int) -> User:
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user


def get_user_by_tg_id(user_id: int) -> User:
    session = Session()
    user = session.query(User).filter(User.telegram_user_id == user_id).first()
    session.close()
    return user


def create_user(telegram_user_id: int, created_at: datetime) -> tuple[User, str]:
    session = Session()
    user_exists = get_user_by_tg_id(telegram_user_id)
    if not user_exists:
        comment = "new"
        user = User(telegram_user_id=telegram_user_id, created_at=created_at)
        session.add(user)
        session.commit()
        session.refresh(user)
        session.close()
        return user, comment
    comment = "exists"
    return user_exists, comment


def get_all_users() -> list[Type[User]]:
    session = Session()
    users = session.query(User).all()
    session.close()
    return users


def update_user1(user_id: int, telegram_user_id: str, telegram_chat_id: str) -> User:
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    user.telegram_user_id = telegram_user_id
    user.telegram_chat_id = telegram_chat_id
    session.commit()
    session.refresh(user)
    session.close()
    return user


def update_user(user_id: int, field: str, new_value) -> User:
    print(user_id)
    session = Session()
    user = session.query(User).filter(User.telegram_user_id == user_id).first()
    if field == 'city':
        user.city = new_value

    session.commit()
    session.refresh(user)
    session.close()
    return user


def add_child(user_id: int, birth_date: datetime, sex: str):
    try:
        db = Session()
        user = get_user_by_tg_id(user_id)

        age_in_days = calculate_age_in_days(birth_date)
        child = Child(
            age=age_in_days,
            sex=sex,
            parent=user
        )

        db.add(child)
        user.children.append(child)
        db.commit()
        db.refresh(user)
        db.close()
        return child
    except:
        print("Something bad happened when adding child")
        return False


def add_bookmark(user_id: int, tip_id: int):
    session = Session()
    user = session.query(User).filter(User.telegram_user_id == user_id).first()

    bookmark = Bookmark(
        user_id=user.id,
        bookmarked_tip_id=tip_id
    )

    session.add(bookmark)
    user.bookmarks.append(bookmark)
    session.commit()
    session.refresh(user)
    session.close()

def get_my_bookmarks(user_id: int):
    session = Session()
    user = get_user_by_tg_id(user_id)
    bookmarks = session.query(Bookmark).filter(Bookmark.user_id == user.id).all()
    session.close()
    return bookmarks


def delete_user(user_id: int) -> None:
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    session.delete(user)
    session.commit()
    session.close()
