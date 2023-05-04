from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from config import AVAILABLE_AGES
get_ages_cb = CallbackData("get_age", "from_day", "until_day")

def ages_keyboard():
    mark = InlineKeyboardMarkup()

    age_buttons = [InlineKeyboardButton(text=age[0],
                                        callback_data=get_ages_cb.new(
                                            from_day=age[1],
                                            until_day=age[2])
                                        )

                   for age in AVAILABLE_AGES]

    cancel = InlineKeyboardButton(text="На главную", callback_data=get_ages_cb.new(
        from_day='back',
        until_day='back')
    )

    mark.add(*age_buttons)
    mark.add(cancel)

    return mark


def before_birth_categories():
    mark = InlineKeyboardMarkup()

    prepare_to_labor = InlineKeyboardButton(
        text="Подготовка к родам",
        callback_data="prepare_to_labor"
    )
