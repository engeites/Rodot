from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from typing import List, Type
from .models import User, Child, Bookmark
from .db import engine


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
    user_exists: User = get_user_by_tg_id(telegram_user_id)
    if not user_exists or not user_exists.passed_basic_reg:
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
    db = Session()
    try:
        # TODO: Если юзер вручную вобьет команду запускающую этот хэндлер, то сможет создать ещё одну запись в базе с ребенком.
        #   нужно проверять есть ли уже ребенок у юзера и если да, возвращать отписку с приглашением изменить данные в профиле

        user = get_user_by_tg_id(user_id)

        child = Child(
            age=birth_date,
            sex=sex,
            parent=user
        )

        db.add(child)
        user.children.append(child)
        user.passed_basic_reg = True
        db.commit()
        db.refresh(user)
        return child
    finally:
        db.close()

    # except:
    #     print("Something bad happened when adding child")
    #     return False


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


def get_user_child(user_id: int):
    session = Session()
    user = session.query(User).filter(User.telegram_user_id == user_id).first()

    if user:
        # get children's age and sex for the user ID
        children_info = session.query(Child.age, Child.sex).filter(Child.parent_id == user.id).first()
        return children_info
    else:
        print("User not found.")


def get_child_advice(session, child_id):
    child = session.query(Child).get(child_id)
    advice = child.advice
    return [a.advice for a in advice]


def check_if_user_passed_reg(user_id: int) -> bool:
    session = Session()
    reg_passed = session.query(User.passed_basic_reg).filter(User.telegram_user_id == user_id).first()
    return reg_passed[0]

def delete_user(user_id: int) -> None:
    session = Session()
    try:
        session.begin()
        # Get the user model
        user = session.query(User).filter_by(User.telegram_user_id == user_id).first()

        # Delete related entries in other tables
        session.query(Bookmark).filter_by(Bookmark.user_id == user.id).delete()
        session.query(Child).filter_by(Child.parent_id == user.id).delete()
        session.query(User).filter_by(User.id == user.id).delete()

    except IntegrityError as e:
        session.rollback()
        # Log the error here

    finally:
        session.close()
        # Log successfully deleted user


def update_user_last_seen(user_id):
    session = Session()

    user = session.query(User).filter_by(telegram_user_id=user_id).first()
    user.last_seen = datetime.now()

    session.commit()

def get_active_users(hours_days: str, time_range: int) -> int:
    session = Session()

    now = datetime.now()
    if hours_days == 'hours':
        time_range = now - timedelta(hours=time_range)
    elif hours_days == 'days':
        time_range = now - timedelta(days=time_range)

    # Query the database for active users
    active_users = session.query(User).filter(User.last_seen >= time_range).all()
    return len(active_users)
