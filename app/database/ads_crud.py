from datetime import datetime, timedelta

from sqlalchemy.orm import sessionmaker, subqueryload
from sqlalchemy import or_
from sqlalchemy.sql import text, func, and_
from typing import List
from .models import ParentingTip, AdvertisementLog, Advertisement
from .db import engine

from app.utils.validators import get_tags_from_str, add_days_to_today_utc

Session = sessionmaker(bind=engine)

from datetime import datetime


def add_advertisement_to_tip(tip_id, ad_text, vendor, active_period):
    session = Session()
    tip = session.query(ParentingTip).filter_by(id=tip_id).one()

    end_date = add_days_to_today_utc(active_period)

    new_ad = Advertisement(
        name=ad_text,
        vendor_name=vendor,
        start_date=datetime.utcnow(),
        end_date=end_date,
        parenting_tip=tip
    )

    session.add(new_ad)
    session.commit()


def add_advertisement_log(parenting_tip_id: int):

    session = Session()
    # Query for Advertisement object using parenting_tip_id
    advertisement = session.query(Advertisement).filter(Advertisement.tip_id == parenting_tip_id).first()

    # Create new AdvertisementLog object
    # ad_log = AdvertisementLog(ad=advertisement, showed_at=datetime.utcnow(), parenting_tip_id=parenting_tip_id)
    ad_log = AdvertisementLog(ad_id=advertisement.id, showed_at=datetime.utcnow(), parenting_tip_id=parenting_tip_id)

    # Add new AdvertisementLog object to session and commit changes
    session.add(ad_log)
    session.commit()


def count_ad_shows(tip_id: int) -> dict|None:
    """
    Counts the number of times an advertisement was shown for the given ParentingTip ID,
    broken down by time period.
    Returns a dictionary with keys 'today', 'yesterday', 'last_week', 'last_month',
    and 'all_time', each containing the respective count as an integer.
    """
    # Get the ParentingTip instance by ID
    session = Session()

    tip: ParentingTip = session.query(ParentingTip).get(tip_id)
    if not tip:
        raise ValueError(f"No ParentingTip found with ID {tip_id}")

    if not tip.advertisement:
        raise ValueError(f"Current Tip has no ad at the moment.")

    # Get the current time
    now = datetime.now()

    # Define time periods
    today = now.date()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)

    # Get counts for each time period
    today_count = session.query(func.count(AdvertisementLog.id)).filter(
        AdvertisementLog.tip_id == tip_id,
        text("DATE_TRUNC('day', advertisement_log.showed_at) = :today")
    ).params(today=today).scalar()

    yesterday_count = session.query(func.count(AdvertisementLog.id)).filter(
        AdvertisementLog.tip_id == tip_id,
        text("DATE_TRUNC('day', advertisement_log.showed_at) = :yesterday")
    ).params(yesterday=yesterday).scalar()

    last_week_count = session.query(func.count(AdvertisementLog.id)).filter(
        AdvertisementLog.tip_id == tip_id,
        text("advertisement_log.showed_at >= :last_week")
    ).params(last_week=last_week).scalar()

    last_month_count = session.query(func.count(AdvertisementLog.id)).filter(
        AdvertisementLog.tip_id == tip_id,
        text("advertisement_log.showed_at >= :last_month")
    ).params(last_month=last_month).scalar()

    all_time_count = session.query(func.count(AdvertisementLog.id)).filter(
        AdvertisementLog.tip_id == tip_id
    ).scalar()

    # Create and return the results dictionary
    results = {
        'today': today_count,
        'yesterday': yesterday_count,
        'last_week': last_week_count,
        'last_month': last_month_count,
        'all_time': all_time_count
    }

    return results