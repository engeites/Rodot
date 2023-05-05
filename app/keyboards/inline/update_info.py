from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

cb = CallbackData("edit", "field", "alias")

def edit_info_keyboard():
    mark = InlineKeyboardMarkup()

    city_change_button = InlineKeyboardButton(
        text="Изменить город",
        callback_data=cb.new(field="city", alias="city")
    )

    birthdate_change_button = InlineKeyboardButton(
        text="Изменить дату рождения ребёнка",
        callback_data=cb.new(field="birthdate", alias="birthdate")
    )

    mark.add(city_change_button).add(birthdate_change_button)
    return mark