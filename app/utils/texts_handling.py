from app.database.models import DailyTip


def handle_daily_article(article_model: DailyTip) -> dict:
    try:
        payload = {
            'media': article_model.media,
            'header': article_model.header,
            'body': article_model.body
        }

    except AttributeError:
        payload = {
            'media': False,
            'header': article_model.header,
            'body': article_model.body
        }
    
    return payload

