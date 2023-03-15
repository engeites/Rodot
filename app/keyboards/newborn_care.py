from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def newborn_care_keyboard():

    # create a custom keyboard
    newborn_kb = ReplyKeyboardMarkup(resize_keyboard=True)

    # create buttons for each option
    bathing_tips_btn = KeyboardButton('Купание')
    diapering_basics_btn = KeyboardButton('Гигиена и подгузники')
    soothing_techniques_btn = KeyboardButton('Плач и успокоение')
    common_concerns_btn = KeyboardButton('Разное')


    # add buttons to the custom keyboard
    newborn_kb.add(bathing_tips_btn, diapering_basics_btn)
    newborn_kb.add(soothing_techniques_btn, common_concerns_btn)

    return newborn_kb
