from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

cb = CallbackData("edit", "field", "alias")

def edit_info_keyboard():
    mark = InlineKeyboardMarkup()

    city_button = InlineKeyboardButton(
        text="Edit city",
        callback_data=cb.new(field="city", alias="city")
    )

    mark.add(city_button)
    return mark