from sqlite3 import IntegrityError

from sqlalchemy.orm import sessionmaker
from .models import DailyTip

from .db import engine

Session = sessionmaker(bind=engine)

def get_list_of_daily_tips() -> list:
    db = Session()
    # Get list of db.models.DailyTip objects
    all_tips = db.query(DailyTip).all()

    return [f"{tip.header} - {tip.id}\n" for tip in all_tips]


def delete_daily_tip_by_id(daily_tip_id: int):
    session = Session()
    daily_tip: DailyTip = session.query(DailyTip).get(daily_tip_id)
    if not daily_tip:
        raise ValueError(f"No advertisement found with ID {daily_tip_id}")

    # Delete the tip
    session.delete(daily_tip)
    session.commit()
    return True

def create_daily_tip(**qwargs) -> DailyTip:
    db = Session()
    daily_tip: DailyTip = DailyTip(
        header=qwargs['header'],
        body=qwargs['body'],
        age_in_days=qwargs['age_in_days'],
        media=qwargs['file_id']
    )

    db.add(daily_tip)
    db.commit()
    db.refresh(daily_tip)
    return daily_tip


def get_daily_tip_by_id(daily_tip_id: int) -> DailyTip:
    session = Session()
    try:
        daily_tip: DailyTip = session.query(DailyTip).get(daily_tip_id)
        return daily_tip
    finally:
        session.close()