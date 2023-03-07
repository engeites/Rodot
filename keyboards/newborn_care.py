from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def newborn_care_keyboard():

    # create a custom keyboard
    newborn_kb = ReplyKeyboardMarkup(resize_keyboard=True)

    # create buttons for each option
    bathing_tips_btn = KeyboardButton('Bathing Tips')
    diapering_basics_btn = KeyboardButton('Diapering Basics')
    soothing_techniques_btn = KeyboardButton('Soothing Techniques')
    common_concerns_btn = KeyboardButton('Common Concerns')


    # add buttons to the custom keyboard
    newborn_kb.add(bathing_tips_btn, diapering_basics_btn)
    newborn_kb.add(soothing_techniques_btn, common_concerns_btn)

    return newborn_kb
