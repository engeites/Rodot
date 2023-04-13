
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


from config import INITIAL_CHOICE, CATEGORIES
from app.extentions import ADMINS

def main_keyboard_unregistered():

    buttons = [InlineKeyboardButton(text=button[0], callback_data=button[1]) for button in INITIAL_CHOICE]

    unreg_main_kb = InlineKeyboardMarkup(row_width=2)
    unreg_main_kb.add(*buttons)
    return unreg_main_kb


def main_keyboard_registered(user_id: int):

    btn_list = CATEGORIES.copy()
    btn_list.append(['🐾 Выбрать возраст', 'Выбрать возраст'])

    my_profile_btn = InlineKeyboardButton(text='⬆️ В профиль', callback_data='⬆️ В профиль')
    help_btn = InlineKeyboardButton(text='Помощь', callback_data='Помощь')
    admin_panel_btn = InlineKeyboardButton(text='Админка', callback_data='admin_menu')

    reg_main_kb = InlineKeyboardMarkup(row_width=2)

    main_buttons = [InlineKeyboardButton(text=name[0], callback_data=name[1]) for name in btn_list]

    if user_id in ADMINS:
        reg_main_kb.add(admin_panel_btn)

    reg_main_kb.add(my_profile_btn)

    reg_main_kb.add(*main_buttons)
    reg_main_kb.add(help_btn)
    return reg_main_kb


def show_categories():

    cancel = InlineKeyboardButton(text='На главную', callback_data='На главную')

    categories_kb = InlineKeyboardMarkup(row_width=2)

    main_buttons = [InlineKeyboardButton(text=name[0], callback_data=name[1]) for name in CATEGORIES]

    categories_kb.add(*main_buttons)
    categories_kb.add((cancel))

    return categories_kb

initial_kb = main_keyboard_unregistered()
categories_kb = show_categories()
