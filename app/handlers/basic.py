import datetime
import unicodedata

from contextlib import suppress
from aiogram import types
from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import MessageNotModified

from app.keyboards.inline.ages import ages_keyboard, cb
from app.keyboards.inline.main_kb_inline import main_kb_registered

from app.texts.basic import choose_age, choose_category

from app.keyboards.inline.main_kb_inline import initial_kb, main_kb_unregistered, main_keyboard_registered, categories_kb

from app.database import user_crud
from app.database import tips_crud

from app.utils.validators import validate_category

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.texts.main_menu import main_menu_unregistered, main_menu_registered
from app.texts.basic import welcome_unreg, welcome_reg, our_philosophy, help_message_reg, help_message_unreg
from app.texts.article_search_texts import category_not_found

from app.config import CATEGORIES
from app.handlers.articles import callback_data
# callback_data = CallbackData('articles', 'id')
from app.keyboards.inline.bookmarks import add_bookmark_keyboard

from app.handlers.articles import AgeAndCategory

class AgeAndTheme(StatesGroup):
    from_day = State()
    until_day = State()
    category = State()


async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    print(user_id)
    created_at = datetime.datetime.now()
    user, comment = user_crud.create_user(user_id, created_at)
    print(f"comment = {comment}")
    if comment == 'exists':
        await message.answer(welcome_reg, reply_markup=main_kb_registered)
        return

    await message.answer(welcome_unreg, reply_markup=initial_kb)


async def show_ages_keyboard(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(AgeAndTheme.from_day.state)
    await call.message.edit_text(choose_age, reply_markup=ages_keyboard)


async def get_age(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    start_age = callback_data['from_day']
    end_age = callback_data['until_day']
    # TODO: Validate if message was from the given keyboard, CRITICAL
    await state.update_data(from_day=start_age, until_day=end_age)
    await call.message.edit_text(choose_category, reply_markup=categories_kb)
    await state.set_state(AgeAndTheme.category.state)


async def get_category(call: types.CallbackQuery, state:FSMContext):
    given_category = call.data
    print(given_category)
    if given_category not in CATEGORIES:
        await call.message.edit_text(category_not_found, reply_markup=categories_kb)
        # TODO: Выше я вызвал kb_registered, но не факт что юзер на самом деле уже зарегистрирован
        return

    await state.update_data(category=validate_category(given_category))
    print("Get category state data: ")
    print(await state.get_data())
    state_data = await state.get_data()

    # Search for article that suits the given age and category
    tips = tips_crud.get_tips_by_multiple_tags([state_data['category']],
                                               int(state_data['from_day']),
                                               int(state_data['until_day']))


    mark = InlineKeyboardMarkup()

    for tip in tips:
        mark.add(InlineKeyboardButton(
            text=tip.header,
            callback_data=callback_data.new(str(tip.id))
        ))

    mark.add(InlineKeyboardButton(
        text="Назад",
        callback_data="Назад"
    ),
        InlineKeyboardButton(
            text="На главную",
            callback_data="На главную"
    ))

    # Return list of articles in inline keyboard
    await call.message.edit_text(f"По выбранным фильтрам есть следующие статьи", reply_markup=mark)
    # await state.finish()


async def go_back_to_articles(call: types.CallbackQuery, state: FSMContext):
    print(state.get_state())
    print(state.get_data())
    if state:
        await state.finish()
    # await state.set_state(AgeAndTheme.category.state)
    # await call.message.edit_caption(choose_category, reply_markup=categories_kb)
    await call.message.edit_text(choose_category, reply_markup=categories_kb)


async def go_to_main(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    user_registered = user_crud.check_if_user_passed_reg(call.from_user.id)
    print(user_registered)

    if user_registered:
        await call.message.edit_text(main_menu_registered, reply_markup=main_kb_registered)
    else:
        await call.message.edit_text(main_menu_unregistered, reply_markup=main_kb_unregistered)


async def send_article_text(call: types.CallbackQuery, callback_data: dict):
    post_id = callback_data["id"]

    article = tips_crud.get_tip_by_id(post_id)
    text = f"<b>{article.header}</b> \n\n"
    text += article.tip
    text += "\n\n"
    # tags = article.tags
    #
    # for tag in tags:
    #     text += " #" + tag.name.strip()
    await call.message.edit_text(text, reply_markup=add_bookmark_keyboard(article.id))

async def send_our_philosophy(call: types.CallbackQuery):
    with suppress(MessageNotModified):
        await call.message.edit_text(our_philosophy, reply_markup=initial_kb)

async def send_help_message_reg(call: types.CallbackQuery):
    await call.message.edit_text(help_message_reg, reply_markup=main_kb_registered)

async def send_help_message_unreg(call: types.CallbackQuery):
    await call.message.edit_text(help_message_unreg, reply_markup=main_kb_unregistered)

async def void_messages(message: types.Message):
    print("Got this message that does not suit other handlers: ")
    print(message.text)
    await message.answer("на " + message.text + " у меня нет ответа")


async def show_prenatal_articles(call: types.CallbackQuery):
    print("Showing prenatal articles")
    print(call.data)
    tips = tips_crud.get_tips_by_multiple_tags(['До родов'], 0, 0)

    mark = InlineKeyboardMarkup()

    for tip in tips:
        mark.add(InlineKeyboardButton(
            text=tip.header,
            callback_data=callback_data.new(str(tip.id))
        ))

    mark.add(InlineKeyboardButton(
        text="Назад",
        callback_data="Назад"
    ),
        InlineKeyboardButton(
            text="На главную",
            callback_data="На главную"
        ))

    # Return list of articles in inline keyboard
    await call.message.edit_text(f"По выбранным фильтрам есть следующие статьи", reply_markup=mark)
    # await state.finish()

def register_basic_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])

    dp.register_callback_query_handler(show_ages_keyboard, Text(equals='🐾 Выбрать возраст'), state="*")
    dp.register_callback_query_handler(go_to_main, cb.filter(from_day='back'), state=AgeAndTheme.from_day)

    dp.register_callback_query_handler(show_prenatal_articles, cb.filter(from_day='0', until_day='0'), state=AgeAndTheme.from_day)
    dp.register_callback_query_handler(get_age, cb.filter(), state=AgeAndTheme.from_day)
    dp.register_callback_query_handler(get_category, Text(equals=CATEGORIES), state=AgeAndTheme.category)
    dp.register_callback_query_handler(send_article_text, callback_data.filter(), state=AgeAndTheme.category)
    dp.register_callback_query_handler(send_article_text, callback_data.filter(), state=AgeAndCategory.data)
    dp.register_callback_query_handler(go_back_to_articles, Text(equals="Назад"), state=AgeAndTheme.category)
    dp.register_callback_query_handler(go_back_to_articles, Text(equals="Назад"), state="*")

    dp.register_callback_query_handler(send_our_philosophy, Text(equals="🧑🏻‍🎓 Наша философия"))
    # dp.register_message_handler(go_to_main, Text(equals="На главную"), state="*")
    dp.register_callback_query_handler(go_to_main, Text(equals="На главную"), state="*")
    dp.register_callback_query_handler(send_help_message_unreg, Text(equals="Как пользоваться ботом"))
    dp.register_callback_query_handler(send_help_message_reg, Text(equals="Помощь"))
    # dp.register_message_handler(go_to_main, commands=['cancel'], state="*")
    dp.register_message_handler(void_messages)