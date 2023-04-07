from sqlalchemy.orm import sessionmaker
from app.database.models import UserArticle
from app.database.db import engine
from datetime import datetime, timedelta
from sqlalchemy import func, distinct

Session = sessionmaker(bind=engine)

def log_article_read(user_tg_id, article_id):
    print(f"Article read by user: {user_tg_id}, article ID = {article_id}")
    session = Session()

    reading_event = UserArticle(user_id=user_tg_id, article_id=article_id, created_at=datetime.utcnow())
    session.add(reading_event)

    session.commit()


def get_article_statistics_old(article_id):
    session = Session()
    # Get the current date and time
    now = datetime.now()

    # Calculate the start and end dates for the different time periods
    today_start = datetime(now.year, now.month, now.day)
    yesterday_start = today_start - timedelta(days=1)
    last_week_start = today_start - timedelta(days=7)
    last_month_start = today_start - timedelta(days=30)

    # Query the database for the number of readings within each time period
    today_count = session.query(func.count(UserArticle.id)).filter_by(article_id=article_id).filter(UserArticle.created_at >= today_start).scalar()
    yesterday_count = session.query(func.count(UserArticle.id)).filter_by(article_id=article_id).filter(UserArticle.created_at >= yesterday_start, UserArticle.created_at < today_start).scalar()
    last_week_count = session.query(func.count(UserArticle.id)).filter_by(article_id=article_id).filter(UserArticle.created_at >= last_week_start).scalar()
    last_month_count = session.query(func.count(UserArticle.id)).filter_by(article_id=article_id).filter(UserArticle.created_at >= last_month_start).scalar()
    total_count = session.query(func.count(UserArticle.id)).filter_by(article_id=article_id).scalar()

    # Return the statistics as a dictionary
    return {
        'today': today_count,
        'yesterday': yesterday_count,
        'last_week': last_week_count,
        'last_month': last_month_count,
        'total': total_count
    }


def get_article_statistics(article_id):
    session = Session()
    # Get the current date and time
    now = datetime.now()

    # Calculate the start and end dates for the different time periods
    today_start = datetime(now.year, now.month, now.day)
    yesterday_start = today_start - timedelta(days=1)
    last_week_start = today_start - timedelta(days=7)
    last_month_start = today_start - timedelta(days=30)

    # Query the database for the number of unique readings within each time period
    today_count = session.query(func.count(distinct(UserArticle.user_id))).filter_by(article_id=article_id).filter(UserArticle.created_at >= today_start).scalar()
    yesterday_count = session.query(func.count(distinct(UserArticle.user_id))).filter_by(article_id=article_id).filter(UserArticle.created_at >= yesterday_start, UserArticle.created_at < today_start).scalar()
    last_week_count = session.query(func.count(distinct(UserArticle.user_id))).filter_by(article_id=article_id).filter(UserArticle.created_at >= last_week_start).scalar()
    last_month_count = session.query(func.count(distinct(UserArticle.user_id))).filter_by(article_id=article_id).filter(UserArticle.created_at >= last_month_start).scalar()
    total_count = session.query(func.count(distinct(UserArticle.user_id))).filter_by(article_id=article_id).scalar()

    # Return the statistics as a dictionary
    return {
        'today': today_count,
        'yesterday': yesterday_count,
        'last_week': last_week_count,
        'last_month': last_month_count,
        'total': total_count
    }