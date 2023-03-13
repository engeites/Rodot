from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def ages_keyboard() -> ReplyKeyboardMarkup:
    mark = ReplyKeyboardMarkup(resize_keyboard=True)

    m_0_3 = KeyboardButton('0-3 months')
    m_3_6 = KeyboardButton('3-6 months')
    m_6_9 = KeyboardButton('6-9 months')
    m_9_12 = KeyboardButton('9-12 months')
    m_12_15 = KeyboardButton('12-15 months')
    m_15_18 = KeyboardButton('15-18 months')
    for_my_child = KeyboardButton('For my child')
    back = KeyboardButton('Go to Main')

    mark.add(m_0_3, m_3_6)
    mark.add(m_6_9, m_9_12)
    mark.add(m_12_15, m_15_18)
    mark.add(for_my_child, back)

    return mark


def categories_keyboard() -> ReplyKeyboardMarkup:
    mark = ReplyKeyboardMarkup(resize_keyboard=True)
    mark.add(KeyboardButton('Health and Security'), KeyboardButton('Feeding'))
    mark.add(KeyboardButton('Sleeping and Schedule'), KeyboardButton('Developmental Activities'))
    mark.add(KeyboardButton('Books and Toys'), KeyboardButton('Outdated Advice'))
    mark.add(KeyboardButton("Go to Main"))

    return mark