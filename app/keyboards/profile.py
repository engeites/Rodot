from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

def profile_keyboard():
    info_upd = KeyboardButton('Обновить данные')
    search_article = KeyboardButton('Поиск по статьям')
    saved_articles = KeyboardButton('Сохранённые статьи')
    my_child = KeyboardButton('Мой ребёнок')
    my_city = KeyboardButton('Мой город')
    day_to_day_service = KeyboardButton('День за днём')
    go_to_main = KeyboardButton('На главную')
    mark = ReplyKeyboardMarkup(resize_keyboard=True)
    mark.add(my_child, my_city)
    mark.add(saved_articles, search_article)
    mark.add(info_upd, day_to_day_service)
    mark.add(go_to_main)
    return mark