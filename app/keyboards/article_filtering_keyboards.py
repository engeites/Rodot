from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def ages_keyboard() -> ReplyKeyboardMarkup:
    mark = ReplyKeyboardMarkup(resize_keyboard=True)
    m_0_0 = KeyboardButton('Новорожденный')
    m_0_3 = KeyboardButton('0-3 месяцев')
    m_3_6 = KeyboardButton('3-6 месяцев')
    m_6_9 = KeyboardButton('6-9 месяцев')
    m_9_12 = KeyboardButton('9-12 месяцев')
    m_12_15 = KeyboardButton('12-15 месяцев')
    m_15_18 = KeyboardButton('15-18 месяцев')
    # for_my_child = KeyboardButton('Для моего ребёнка')
    back = KeyboardButton('На главную')

    mark.add(m_0_0, m_0_3)
    mark.add(m_3_6, m_6_9)
    mark.add(m_9_12, m_12_15)
    mark.add(m_15_18, back)

    return mark


def categories_keyboard() -> ReplyKeyboardMarkup:
    mark = ReplyKeyboardMarkup(resize_keyboard=True)
    mark.add(KeyboardButton('Здоровье и гигиена'), KeyboardButton('Кормление'))
    mark.add(KeyboardButton('Сон и режим'), KeyboardButton('Игры и развитие'))
    mark.add(KeyboardButton('Книги и игрушки'), KeyboardButton('Вредные советы'))
    mark.add(KeyboardButton('Полезные покупки'), KeyboardButton("На главную"))

    return mark