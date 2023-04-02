
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


from sqlalchemy.exc import IntegrityError

def delete_child_advice(advice_id):
    session = Session()

    try:
        with session.begin():
            advice = session.query(ChildAdvice).filter_by(id=advice_id).first()

            if not advice:
                # Raise an error if the advice with the given id does not exist
                raise ValueError(f"No ChildAdvice found with id {advice_id}")

            session.delete(advice)

        session.commit()

    except IntegrityError:
        # If there is an error during the transaction, rollback the session
        session.rollback()
        raise

    finally:
        session.close()