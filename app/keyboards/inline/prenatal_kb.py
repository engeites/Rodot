
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from config import INITIAL_CHOICE, MAIN_KB_UNREG_BTNS, CATEGORIES, PRENATAL_CATEGORIES
from app.extentions import ADMINS

prenatal_categories_cb = CallbackData('prenatal', 'category')


def render_prenatal_keyboard() -> InlineKeyboardMarkup:
    mark = InlineKeyboardMarkup(row_width=1)

    buttons = [InlineKeyboardButton(text=button[0],
                                    callback_data=prenatal_categories_cb.new(
                                        category=button[1])
                                    )
               for button in PRENATAL_CATEGORIES]

    go_back = InlineKeyboardButton(
        text="Назад",
        callback_data="На главную"
    )

    mark.add(*buttons).add(go_back)
    return mark

prenatal_kb = render_prenatal_keyboard()