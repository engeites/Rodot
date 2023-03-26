from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from app.config import CATEGORIES

def initial_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    go_to_profile = KeyboardButton("Заполнить профиль")
    see_ages = KeyboardButton("🐾 Выбрать возраст")
    how_to_use_bot = KeyboardButton("Наша философия")

    kb.add(go_to_profile, see_ages).add(how_to_use_bot)
    return kb


def main_keyboard_unregistered():

    # create a custom keyboard
    custom_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    # create buttons for each option
    my_profile_btn = KeyboardButton('Заполнить профиль')
    # newborn_care_btn = KeyboardButton('Забота о новорожденном')
    # feeding_tips_btn = KeyboardButton('Подготовка к родам')
    choose_age_btn = KeyboardButton('🐾 Выбрать возраст')
    help_btn = KeyboardButton('Как пользоваться ботом')
    contact_btn = KeyboardButton('Связаться с нами')

    # add buttons to the custom keyboard
    custom_keyboard.add(my_profile_btn, choose_age_btn)
    custom_keyboard.add(choose_age_btn)
    custom_keyboard.add(help_btn, contact_btn)

    return custom_keyboard

def main_keyboard_registered():

    # create a custom keyboard
    custom_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    my_profile_btn = KeyboardButton('В профиль')
    custom_keyboard.add(my_profile_btn)

    for category in CATEGORIES:
        custom_keyboard.add(category)

    # create buttons for each option
    # my_profile_btn = KeyboardButton('В профиль')
    # newborn_care_btn = KeyboardButton('Здоровье и гигиена')
    # feeding_tips_btn = KeyboardButton('Игры и развитие')
    # developmental_activities_btn = KeyboardButton('Полезные покупки')
    help_btn = KeyboardButton('Помощь')
    contact_btn = KeyboardButton('🐾 Выбрать возраст')

    custom_keyboard.add(help_btn, contact_btn)

    # # add buttons to the custom keyboard
    # custom_keyboard.add(my_profile_btn, newborn_care_btn)
    # custom_keyboard.add(feeding_tips_btn, developmental_activities_btn)
    # custom_keyboard.add(help_btn, contact_btn)

    return custom_keyboard
