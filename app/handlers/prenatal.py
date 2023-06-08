from contextlib import suppress

from aiogram import types
from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified

from app.handlers.basic import AgeAndTheme
from app.keyboards.inline.ages import get_ages_cb

from app.keyboards.inline.prenatal_kb import prenatal_kb, prenatal_categories_cb

from app.utils.form_tip_list import form_tip_list


async def show_prenatal_categories(call: types.CallbackQuery):
    with suppress(MessageNotModified):

        # Show categories for prenatal period

        await call.message.edit_text("Здесь перечислены категории статей, которые лучше прочитать до родов",
                                     reply_markup=prenatal_kb)


async def show_tips_for_category(call: types.CallbackQuery, callback_data: dict):
    search_criteria = {
        'category': callback_data['category'],
        'from_day': 0,
        'until_day': 0
    }

    reply_mark: InlineKeyboardMarkup = form_tip_list(search_criteria)

    reply_mark.add(InlineKeyboardButton(
        text="< Назад",
        callback_data="back_to_prenatal_categories"
    ),
        InlineKeyboardButton(
            text="На главную",
            callback_data="На главную"
        ))

    await call.message.edit_text("Вот что я нашёл по запросу",
                                 reply_markup=reply_mark)


def register_prenatal_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(show_prenatal_categories, get_ages_cb.filter(from_day='0', until_day='0'), state=AgeAndTheme.from_day)
    dp.register_callback_query_handler(show_prenatal_categories, Text(equals="back_to_prenatal_categories"), state="*")
    dp.register_callback_query_handler(show_tips_for_category, prenatal_categories_cb.filter(), state="*")
