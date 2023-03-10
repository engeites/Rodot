from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def initial_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    go_to_profile = KeyboardButton("Get a profile")
    see_ages = KeyboardButton("Choose age")
    how_to_use_bot = KeyboardButton("Our philosophy")

    kb.add(go_to_profile, see_ages).add(how_to_use_bot)
    return kb


def categories_keyboard():

    # create a custom keyboard
    custom_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    # create buttons for each option
    my_profile_btn = KeyboardButton('My Profile')
    newborn_care_btn = KeyboardButton('Newborn Care')
    feeding_tips_btn = KeyboardButton('Prenatal Preparation')
    developmental_activities_btn = KeyboardButton('Developmental Activities')
    health_safety_btn = KeyboardButton('Health & Safety')
    bad_tips_btn = KeyboardButton('Bad Tips')

    # add buttons to the custom keyboard
    custom_keyboard.add(my_profile_btn, newborn_care_btn)
    custom_keyboard.add(feeding_tips_btn, developmental_activities_btn)
    custom_keyboard.add(health_safety_btn, bad_tips_btn)

    return custom_keyboard
