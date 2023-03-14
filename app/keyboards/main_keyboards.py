from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def initial_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)

    go_to_profile = KeyboardButton("Get a profile")
    see_ages = KeyboardButton("Choose age")
    how_to_use_bot = KeyboardButton("Our philosophy")

    kb.add(go_to_profile, see_ages).add(how_to_use_bot)
    return kb


def main_keyboard():

    # create a custom keyboard
    custom_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    # create buttons for each option
    my_profile_btn = KeyboardButton('My Profile')
    newborn_care_btn = KeyboardButton('Newborn Care')
    feeding_tips_btn = KeyboardButton('Prenatal Preparation')
    developmental_activities_btn = KeyboardButton('Choose Age')
    help_btn = KeyboardButton('How to use this bot')
    contact_btn = KeyboardButton('Contact us')

    # add buttons to the custom keyboard
    custom_keyboard.add(my_profile_btn, newborn_care_btn)
    custom_keyboard.add(feeding_tips_btn, developmental_activities_btn)
    custom_keyboard.add(help_btn, contact_btn)

    return custom_keyboard
