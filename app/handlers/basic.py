import datetime

from contextlib import suppress
from aiogram import types
from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified

from app.extentions import logger
from app.database.user_crud import update_user_last_seen, check_if_user_passed_reg
from app.keyboards.inline.ages import ages_keyboard, get_ages_cb
from app.keyboards.inline.bookmarks import add_advertisement_cb

from app.texts.basic import choose_age, choose_category

from app.keyboards.inline.main_kb_inline import initial_kb, main_keyboard_registered, show_categories
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

from config import ADMINS, CATEGORIES_callback
from app.utils.form_tip_list import render_tip_cb
from app.keyboards.inline.bookmarks import add_bookmark_keyboard

from app.handlers.articles import AgeAndCategory


# TODO: There is a bug: if baby's age in days = 0, bot says that he is too old to use this bot

class AgeAndTheme(StatesGroup):
    from_day = State()
    until_day = State()
    category = State()


async def send_welcome(message: types.Message):
    user_id = message.from_user.id

    new_user = user_crud.create_user(user_id)

    if new_user['already_existed']:
        if new_user['passed_reg']:
            logger.info(f"Start command sent by user {user_id}. User already exists in db. @{message.from_user.username}")
            await message.answer(welcome_reg, reply_markup=main_keyboard_registered(message.from_user.id))
            return

    logger.info(f"New user registered: {user_id}. @{message.from_user.username}")
    await message.answer(welcome_unreg, reply_markup=initial_kb)


async def show_ages_keyboard(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(AgeAndTheme.from_day.state)
    await call.message.edit_text(choose_age, reply_markup=ages_keyboard())

    logger.info(f"User {call.from_user.id} looks for tips for different ages")


async def get_age(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    start_age = callback_data['from_day']
    end_age = callback_data['until_day']

    await state.update_data(from_day=start_age, until_day=end_age)
    await call.message.edit_text(choose_category, reply_markup=show_categories())
    await state.set_state(AgeAndTheme.category.state)

    logger.info(f"User {call.from_user.id} chose age from {start_age} to {end_age} days old")


async def get_category(call: types.CallbackQuery, state:FSMContext):
    given_category = call.data
    category = given_category

    await state.update_data(category=category)


    search_criteria = await state.get_data()

    logger.info(f"User {call.from_user.id} has chosen category: {given_category}")

    reply_markup = form_tip_list(search_criteria)

    reply_markup.add(InlineKeyboardButton(
        text="< Назад",
        callback_data="< Назад"
    ),
        InlineKeyboardButton(
            text="На главную",
            callback_data="На главную"
        ))

    await call.message.edit_text(f"По выбранным фильтрам есть следующие статьи", reply_markup=reply_markup)

    update_user_last_seen(call.from_user.id)


async def  go_back_to_articles(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()

    logger.info(f"User {call.from_user.id} read an article and went back")

    if not data:
        user_registered = check_if_user_passed_reg(call.from_user.id)
        if not user_registered:
            await call.message.edit_text(main_menu_unregistered, reply_markup=initial_kb)
            return
        else:
            await call.message.edit_text(main_menu_registered, reply_markup=main_keyboard_registered(call.from_user.id))
            return

    reply_markup: InlineKeyboardMarkup = form_tip_list(data)

    reply_markup.add(InlineKeyboardButton(
        text="< Назад",
        callback_data="< Назад"
    ),
        InlineKeyboardButton(
            text="На главную",
            callback_data="На главную"
        ))
    await call.message.edit_text("По выбранным фильтрам есть следующие статьи", reply_markup=reply_markup)


async def go_back_to_categories(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(AgeAndTheme.category.state)
    await call.message.edit_text(choose_category, reply_markup=show_categories())


async def go_to_main(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    logger.info("Finished previous state")
    user_registered = user_crud.check_if_user_passed_reg(call.from_user.id)
    if user_registered:
        await call.message.edit_text(main_menu_registered, reply_markup=main_keyboard_registered(call.from_user.id))
    else:
        await call.message.edit_text(main_menu_unregistered, reply_markup=initial_kb)


async def render_tip(call: types.CallbackQuery, callback_data: dict):
    post_id = callback_data["id"]

    tip = tips_crud.get_tip_by_id(post_id)

    formatter = TipRenderer(tip)
    message_text = formatter.form_final_text()

    if call.from_user.id in ADMINS:
        await call.message.edit_text(message_text, reply_markup=add_bookmark_keyboard(tip.id, admin=True))
    else:
        await call.message.edit_text(message_text, reply_markup=add_bookmark_keyboard(tip.id))

    db_analytics.log_article_read(call.from_user.id, tip.id)
    logger.info(f"User {call.from_user.id} read tip: {tip.header}")


async def send_our_philosophy(call: types.CallbackQuery):
    with suppress(MessageNotModified):
        await call.message.edit_text(use_instructions, reply_markup=initial_kb)


async def send_help_message_reg(call: types.CallbackQuery):
    with suppress(MessageNotModified):
        await call.message.edit_text(help_message_reg, reply_markup=main_keyboard_registered(call.from_user.id))


async def send_help_message_unreg(call: types.CallbackQuery):
    await call.message.edit_text(help_message_unreg, reply_markup=initial_kb)


async def void_messages(message: types.Message):
    print("Got this message that does not suit other handlers: ")
    print(message.text)
    await message.answer("на " + message.text + " у меня нет ответа")


def register_basic_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])

    dp.register_callback_query_handler(show_ages_keyboard, Text(equals='Выбрать возраст'), state="*")
    dp.register_callback_query_handler(go_to_main, get_ages_cb.filter(from_day='back'), state=AgeAndTheme.from_day)
    dp.register_callback_query_handler(get_age, get_ages_cb.filter(), state=AgeAndTheme.from_day)

    dp.register_callback_query_handler(get_category, Text(equals=CATEGORIES_callback), state=AgeAndTheme.category)
    dp.register_callback_query_handler(render_tip, render_tip_cb.filter(), state=AgeAndTheme.category)
    dp.register_callback_query_handler(render_tip, render_tip_cb.filter(), state=AgeAndCategory.data)
    dp.register_callback_query_handler(render_tip, render_tip_cb.filter(), state="*")

    dp.register_callback_query_handler(go_back_to_categories, Text(equals="< Назад"), state=AgeAndTheme.category)
    dp.register_callback_query_handler(go_back_to_categories, Text(equals="< Назад"), state=AgeAndCategory.data)
    dp.register_callback_query_handler(go_back_to_articles, Text(equals="Назад"), state=AgeAndTheme.category)
    dp.register_callback_query_handler(go_back_to_articles, Text(equals="Назад"), state="*")

    dp.register_callback_query_handler(send_our_philosophy, Text(equals="Как пользоваться ботом"))
    dp.register_callback_query_handler(go_to_main, Text(equals="На главную"), state="*")
    dp.register_callback_query_handler(send_help_message_unreg, Text(equals="Как пользоваться ботом"))
    dp.register_callback_query_handler(send_help_message_reg, Text(equals="Помощь"))
    # dp.register_message_handler(go_to_main, commands=['cancel'], state="*")
    dp.register_message_handler(void_messages)