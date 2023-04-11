
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from config import INITIAL_CHOICE, MAIN_KB_UNREG_BTNS, CATEGORIES
from app.extentions import ADMINS

prenatal_categories_cb = CallbackData('prenatal', 'category')


def render_prenatal_keyboard() -> InlineKeyboardMarkup:
    mark = InlineKeyboardMarkup()

    prepare_to_due = InlineKeyboardButton(
        text="Подготовка к родам",
        callback_data=prenatal_categories_cb.new(
            category="Подготовка к родам"
        )
    )

    prepare_house = InlineKeyboardButton(
        text="Покупки к рождению малыша",
        callback_data=prenatal_categories_cb.new(
            category="Покупки к рождению малыша"
        )
    )

    prepare_psychology = InlineKeyboardButton(
        text="Подготовка мамы и семьи",
        callback_data=prenatal_categories_cb.new(
            category="Подготовка мамы и семьи"
        )
    )

    go_back = InlineKeyboardButton(
        text="Назад",
        callback_data="GoBack"
    )

    mark.add(prepare_to_due, prepare_house).add(prepare_psychology, go_back)
    return mark

prenatal_kb = render_prenatal_keyboard()