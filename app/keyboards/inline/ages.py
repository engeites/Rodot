from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.config import AVAILABLE_AGES_initial
get_ages_cb = CallbackData("get_age", "from_day", "until_day")

def ages_keyboard():
    mark = InlineKeyboardMarkup()

    age_buttons = [InlineKeyboardButton(text=age[0],
                                        callback_data=get_ages_cb.new(
                                            from_day=age[1],
                                            until_day=age[2])
                                        )

               for age in AVAILABLE_AGES_initial]

    cancel = InlineKeyboardButton(text="На главную", callback_data=get_ages_cb.new(
        from_day='back',
        until_day='back')
    )

    mark.add(*age_buttons)
    mark.add(cancel)

    return mark

ages_keyboard = ages_keyboard()
