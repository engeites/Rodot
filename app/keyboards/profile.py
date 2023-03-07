from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

def profile_keyboard():
    info_upd = KeyboardButton('Update my info')
    search_article = KeyboardButton('Article Search')
    saved_articles = KeyboardButton('My Saved Articles')
    day_to_day_service = KeyboardButton('Day to day support')
    go_to_main = KeyboardButton('Go to main menu')
    mark = ReplyKeyboardMarkup(resize_keyboard=True)
    mark.add(info_upd, search_article).add(saved_articles, day_to_day_service)
    mark.add(go_to_main)
    return mark