from sqlalchemy.orm import sessionmaker
from app.database.models import UserArticle, ParentingTip
from app.database.db import engine
from datetime import datetime, timedelta
from sqlalchemy import func, distinct

from app.extentions import logger

Session = sessionmaker(bind=engine)

def log_article_read(user_tg_id, article_id):
    logger.info(f"Tip read by user: {user_tg_id}, Tip ID = {article_id}")
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


def get_most_viewed_tips():
    session = Session()

    # Get the current date and time
    now = datetime.now()

    # Calculate the start date for the last 7 days
    last_week_start = now - timedelta(days=7)

    # Query the database to get the articles and their view counts within the last 7 days
    articles_query = session.query(UserArticle.article_id,
                                   func.count(distinct(UserArticle.user_id)).label('view_count')) \
        .filter(UserArticle.created_at >= last_week_start) \
        .group_by(UserArticle.article_id) \
        .subquery()

    # Query the database to get the articles with the highest view counts
    top_articles = session.query(ParentingTip, articles_query.c.view_count) \
        .join(articles_query, ParentingTip.id == articles_query.c.article_id) \
        .order_by(articles_query.c.view_count.desc()) \
        .limit(10)  # Adjust the limit based on how many top articles you want

    # Return the articles as a list of dictionaries
    return [
        {
            'article_id': article.id,
            'header': article.header,
            'view_count': view_count
        }
        for article, view_count in top_articles
    ]
