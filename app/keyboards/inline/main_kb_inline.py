from datetime import datetime

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.database.user_crud import get_user_child
from app.keyboards.inline.prenatal_kb import render_prenatal_keyboard, prenatal_categories_cb

from config import INITIAL_CHOICE, CATEGORIES, PRENATAL_CATEGORIES
from app.extentions import ADMINS

def main_keyboard_unregistered():

    buttons = [InlineKeyboardButton(text=button[0], callback_data=button[1]) for button in INITIAL_CHOICE]

    unreg_main_kb = InlineKeyboardMarkup(row_width=2)
    unreg_main_kb.add(*buttons)
    return unreg_main_kb


def main_keyboard_registered(user_id: int):


    child_birthdate: datetime =  get_user_child(user_id)[0]
    # If child_birthdate is in the future, show prenatal menu
    child_age = (datetime.now() - child_birthdate).days / 365
    if child_age < 0:

        updated_PRENATAL_CATEGORIES = PRENATAL_CATEGORIES.copy()
        # updated_PRENATAL_CATEGORIES.append(['🐾 Выбрать возраст', 'Выбрать возраст'])

        main_buttons = [InlineKeyboardButton(text=button[0],
                                        callback_data=prenatal_categories_cb.new(
                                            category=button[1])
                                        )
                   for button in updated_PRENATAL_CATEGORIES]
        main_buttons.append(
            InlineKeyboardButton(text="🐾 Выбрать возраст",
                                 callback_data="Выбрать возраст"
                                 )
        )
        reg_main_kb = InlineKeyboardMarkup(row_width=1)

    else:
        btn_list = CATEGORIES.copy()
        btn_list.append(['🐾 Выбрать возраст', 'Выбрать возраст'])
        main_buttons = [InlineKeyboardButton(text=name[0], callback_data=name[1]) for name in btn_list]
        reg_main_kb = InlineKeyboardMarkup(row_width=2)

    my_profile_btn = InlineKeyboardButton(text='⬆️ В профиль', callback_data='В профиль')
    help_btn = InlineKeyboardButton(text='👨‍👩‍👧‍👦 Сообщество', callback_data='Помощь')
    admin_panel_btn = InlineKeyboardButton(text='Админка', callback_data='admin_menu')



    if user_id in ADMINS:
        reg_main_kb.add(admin_panel_btn)

    reg_main_kb.add(my_profile_btn)

    reg_main_kb.add(*main_buttons)
    reg_main_kb.add(help_btn)
    return reg_main_kb


def show_categories(no_cancel: bool = False):

    cancel = InlineKeyboardButton(text='На главную', callback_data='На главную')

    categories_kb = InlineKeyboardMarkup(row_width=2)

    main_buttons = [InlineKeyboardButton(text=name[0], callback_data=name[1]) for name in CATEGORIES]

    categories_kb.add(*main_buttons)
    if not no_cancel:
        categories_kb.add(cancel)

    return categories_kb

initial_kb = main_keyboard_unregistered()
