from datetime import datetime, timedelta

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.orm import sessionmaker
from typing import Type
from .models import User, Child, Bookmark, AdminUser
from .db import engine
from app.extentions import logger

Session = sessionmaker(bind=engine)


def get_all_users() -> list:
    session = Session()
    # users = session.query(User).all()
    # users = session.query(User).filter(User.is_banned == False, User.blocked_bot == False).with_entities(
    #     User.telegram_user_id).all()

    users = session.query(User).filter(
        or_(
            User.is_banned == False,
            User.is_banned.is_(None)
        ),
        or_(
            User.blocked_bot == False,
            User.blocked_bot.is_(None)
        )
    ).with_entities(User.telegram_user_id).all()
    session.close()
    return users

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


def create_user(telegram_user_id: int) -> dict:
    session = Session()
    user: User = get_user_by_tg_id(telegram_user_id)

    if user:
        if user.passed_basic_reg:
            return {'user': user, 'already_existed': True, 'passed_reg' : True}
        else:
            return {'user': user, 'already_existed': True, 'passed_reg': False}

    new_user = User(telegram_user_id=telegram_user_id, created_at=datetime.utcnow())

    session.add(new_user)
    session.commit()
    session.close()

    return {'user': new_user, 'already_existed': False}


def update_user_old(user_id: int, telegram_user_id: str, telegram_chat_id: str) -> User:
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    user.telegram_user_id = telegram_user_id
    user.telegram_chat_id = telegram_chat_id
    session.commit()
    session.refresh(user)
    session.close()
    return user


def update_user(user_id: int, field: str, new_value) -> User:
    """
    This function updates a column value in User model.
    :param user_id: User.telegram_user_id
    :param field: Which column to update. Should be same as db column name
    :param new_value:
    :return: User model
    """
    session = Session()

    user = session.query(User).filter(User.telegram_user_id == user_id).first()

    if field == 'city':
        user.city = new_value
    if field == 'subscription_end':
        user.subscription_end = new_value


    session.commit()
    session.refresh(user)
    session.close()
    return user


def add_child(user_id: int, birth_date: datetime, sex: str):
    db = Session()

    try:
        user: User = get_user_by_tg_id(user_id)

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

    except IntegrityError:
        # TODO: Need logging here
        db.rollback()

    finally:
        db.close()

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

def update_users_child_birthdate(user_id: int, new_birthdate: datetime) -> bool:

    if not isinstance(new_birthdate, datetime):
        logger.error(f"new_birthdate is not a datetime object. User ID: {user_id}")
        return False

    session = Session()
    user = session.query(User).filter_by(telegram_user_id=user_id).first()

    # If the user is not found, return None
    if not user:
        logger.error(f"Trying to get user ID {user_id} from db. User does not exist")
        return False

    # Get the first child associated with the user
    try:
        child = user.children[0]
        child.age = new_birthdate
        session.commit()
        return True
    except IndexError as e:
        logger.error(f"Trying to get a child of user ID {user_id}. Has no child. \nException: {e}")
        return False


def get_user_child(user_id: int):
    session = Session()
    user = session.query(User).filter(User.telegram_user_id == user_id).first()

    if user:
        # get children's age and sex for the user ID
        children_info = session.query(Child.age, Child.sex).filter(Child.parent_id == user.id).first()
        return children_info
    else:
        logger.error(f"Try to get user's: {user_id} child failed. User does not have registered child")
        return False


def get_child_advice(session, child_id):
    child = session.query(Child).get(child_id)
    advice = child.advice
    return [a.advice for a in advice]


def check_if_user_passed_reg(user_id: int) -> bool:
    session = Session()
    reg_passed = session.query(User.passed_basic_reg).filter(User.telegram_user_id == user_id).first()
    return reg_passed[0]


def set_user_as_admin(user_id: int) -> None:
    session = Session()
    new_admin = AdminUser(username=user_id)

    session.add(new_admin)
    session.commit()
    session.close()





def get_user_registration_stats():
    session = Session()

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    seven_days_ago = today - timedelta(days=7)
    thirty_days_ago = today - timedelta(days=30)

    today_count = session.query(User).filter(User.created_at >= today).count()
    yesterday_count = session.query(User).filter(User.created_at >= yesterday, User.created_at < today).count()
    seven_days_count = session.query(User).filter(User.created_at >= seven_days_ago).count()
    thirty_days_count = session.query(User).filter(User.created_at >= thirty_days_ago).count()
    total_count = session.query(User).count()

    return {
        "today_count": today_count,
        "yesterday_count": yesterday_count,
        "seven_days_count": seven_days_count,
        "thirty_days_count": thirty_days_count,
        "total_count": total_count,
    }


def update_user_city(telegram_user_id, new_city):
    session = Session()
    user = session.query(User).filter_by(telegram_user_id=telegram_user_id).first()
    if user:
        user.city = new_city
        session.commit()
    else:
        print(f"User with telegram_user_id {telegram_user_id} not found")


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


def mark_user_that_blocked_bot(user_id: int):
    session = Session()

    try:
        user = session.query(User).filter_by(telegram_user_id=user_id).one()
        user.blocked_bot = True
        session.commit()
        return True
    except NoResultFound:
        return False