
from sqlalchemy.orm import sessionmaker
from app.database.models import ChildAdvice

from app.database.db import engine

Session = sessionmaker(bind=engine)

def get_advice_for_age(age_in_days):
    session = Session()

    advice = session.query(ChildAdvice).filter(
        ChildAdvice.age_range_start <= age_in_days,
        ChildAdvice.age_range_end >= age_in_days
    ).all()

    return advice


def add_new_advice(age_start, age_end, advice_text):
    session = Session()

    new_advice = ChildAdvice(
        age_range_start=age_start,
        age_range_end=age_end,
        advice=advice_text)

    session.add(new_advice)
    session.commit()
    session.close()