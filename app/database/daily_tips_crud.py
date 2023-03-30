from sqlalchemy.orm import sessionmaker
from .models import DailyTip

from .db import engine

Session = sessionmaker(bind=engine)

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