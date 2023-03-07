from sqlalchemy.orm import sessionmaker
from typing import List, Type
from .models import User
from .db import engine

Session = sessionmaker(bind=engine)


def create_user(telegram_user_id: str, telegram_chat_id: str, created_at) -> User:
    session = Session()
    user = User(telegram_user_id=telegram_user_id, telegram_chat_id=telegram_chat_id, created_at=created_at)
    session.add(user)
    session.commit()
    session.refresh(user)
    session.close()
    return user


def get_user_by_id(user_id: int) -> User:
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    session.close()
    return user


def get_all_users() -> list[Type[User]]:
    session = Session()
    users = session.query(User).all()
    session.close()
    return users


def update_user(user_id: int, telegram_user_id: str, telegram_chat_id: str) -> User:
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    user.telegram_user_id = telegram_user_id
    user.telegram_chat_id = telegram_chat_id
    session.commit()
    session.refresh(user)
    session.close()
    return user


def delete_user(user_id: int) -> None:
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    session.delete(user)
    session.commit()
    session.close()
