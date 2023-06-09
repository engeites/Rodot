from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

cb = CallbackData("set_sex", "sex")

def set_child_sex():
    mark = InlineKeyboardMarkup(row_width=2)

    male_child = InlineKeyboardButton(
        text="Мальчик",
        callback_data=cb.new(sex="male")
    )
    female_child = InlineKeyboardButton(
        text="Девочка",
        callback_data=cb.new(sex="female")
    )
    unknown = InlineKeyboardButton(
        text="Пока не знаю",
        callback_data=cb.new(sex="unknown")
    )


    mark.add(male_child, female_child, unknown)
    return mark