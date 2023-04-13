import datetime

from contextlib import suppress
from aiogram import types
from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified

from app.database.models import ParentingTip
from app.extentions import logger
from app.database.user_crud import update_user_last_seen, check_if_user_passed_reg
from app.handlers.basic import AgeAndTheme
from app.keyboards.inline.ages import ages_keyboard, get_ages_cb
from app.keyboards.inline.bookmarks import add_advertisement_cb
from app.utils.form_tip_list import render_tip_cb
from app.texts.basic import choose_age, choose_category

from app.keyboards.inline.main_kb_inline import initial_kb, initial_kb, main_keyboard_registered, categories_kb
from app.keyboards.inline.prenatal_kb import prenatal_kb, prenatal_categories_cb

from app.database import user_crud
from app.database import tips_crud
from app.database import db_analytics
from app.utils.form_tip_list import form_tip_list
from app.utils.message_renderers import TipRenderer

from app.utils.validators import validate_category

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.texts.main_menu import main_menu_unregistered, main_menu_registered
from app.texts.basic import welcome_unreg, welcome_reg, use_instructions, help_message_reg, help_message_unreg

from config import CATEGORIES, ADMINS
from app.utils.form_tip_list import render_tip_cb
# callback_data = CallbackData('articles', 'id')
from app.keyboards.inline.bookmarks import add_bookmark_keyboard

from app.handlers.articles import AgeAndCategory



async def show_prenatal_categories(call: types.CallbackQuery):
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
