from app.database.models import DailyTip


def handle_daily_article(article_model: DailyTip) -> dict:
    if article_model.media == "":

        payload = {
            'media': False,
            'header': article_model.header,
            'body': article_model.body
        }
        # handle article without media
    else:
        payload = {
            'media': article_model.media,
            'header': article_model.header,
            'body': article_model.body
        }
        # handle article with media
    return payload

