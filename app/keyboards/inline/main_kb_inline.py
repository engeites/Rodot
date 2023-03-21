
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


from app.config import INITIAL_CHOICE, MAIN_KB_UNREG_BTNS, CATEGORIES

buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in INITIAL_CHOICE]

initial_kb = InlineKeyboardMarkup(row_width=2)
initial_kb.add(*buttons)

def main_keyboard_unregistered():

    buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in MAIN_KB_UNREG_BTNS]

    unreg_main_kb = InlineKeyboardMarkup(row_width=2)
    unreg_main_kb.add(*buttons)
    return unreg_main_kb


def main_keyboard_registered():

    btn_list = CATEGORIES.copy()
    btn_list.append('Выбрать возраст')

    my_profile_btn = InlineKeyboardButton(text='В профиль', callback_data='В профиль')
    help_btn = InlineKeyboardButton(text='Помощь', callback_data='Помощь')
    contact_us_btn = InlineKeyboardButton(text='Контакты', callback_data='Контакты')

    reg_main_kb = InlineKeyboardMarkup(row_width=2)
    main_buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in btn_list]

    reg_main_kb.add(my_profile_btn)

    reg_main_kb.add(*main_buttons)
    # reg_main_kb.add(choose_age)
    reg_main_kb.add(help_btn, contact_us_btn)
    return reg_main_kb


def show_categories():

    cancel = InlineKeyboardButton(text='Отмена', callback_data='Отмена')

    categories_kb = InlineKeyboardMarkup(row_width=2)

    main_buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in CATEGORIES]

    categories_kb.add(*main_buttons)
    categories_kb.add((cancel))

    return categories_kb

main_kb_unregistered = main_keyboard_unregistered()
main_kb_registered = main_keyboard_registered()
categories_kb = show_categories()
