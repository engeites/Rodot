from contextlib import suppress
from datetime import datetime
import pickle

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

import app.database.models
from app.keyboards.inline.bookmarks import bookmark_link_cb, all_bookmarks_keyboard, add_bookmark_keyboard
from app.keyboards.profile import profile_keyboard
from app.keyboards.inline.profile_kb_inline import profile_kb
from app.keyboards.inline.bookmarks import add_bookmark_go_back

from app.texts.profile_texts import start_search_text, no_articles_found, list_of_found_articles

from app.database import user_crud, tips_crud
from app.utils.validators import calculate_age_in_days
from app.texts import bookmark_texts, profile_texts

from app.extentions import redis_client

show_article_callback = CallbackData('show_article', 'id')

class SearchState(StatesGroup):
    query = State()

async def profile_menu_inline(call: types.CallbackQuery):
    await call.message.edit_text(profile_texts.profile_introduction,
        reply_markup=profile_kb
    )

async def my_child(call: types.CallbackQuery):

    def get_readable_date(birth_date: datetime) -> str:
         return birth_date.strftime("%d.%m.%Y")

    sex_options = {
        'male': 'мальчик',
        'female': 'девочка'
    }

    user = user_crud.get_user_by_tg_id(call.from_user.id)
    children = user.children

    if children:  # check if there are any children
        child = children[0]  # get the first child in the list

        text = profile_texts.my_child.format(
            get_readable_date(child.age),
            calculate_age_in_days(child.age),
            sex_options[child.sex]
        )
    else:
        text = "You have no registered children"

    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(
        text="В профиль",
        callback_data='В профиль'
    ))

    await call.message.edit_text(text, reply_markup=mark)


async def get_my_bookmarks(call: types.CallbackQuery):

    user_id = call.from_user.id
    keyboard_with_bookmarks = all_bookmarks_keyboard(user_id)
    if not keyboard_with_bookmarks:
        await call.message.answer(bookmark_texts.no_bookmarks_found)
        return
    await call.message.edit_text(list_of_found_articles, reply_markup=keyboard_with_bookmarks)


async def show_bookmarked_tip(call: types.CallbackQuery, callback_data: dict):

    mark = InlineKeyboardMarkup(row_width=1)

    mark.add(InlineKeyboardButton(
        text="< Назад к списку",
        callback_data='< Назад к списку'
    ))

    article = tips_crud.get_tip_by_id(callback_data['tip_id'])
    text = article.header
    text += "\n\n"
    text += article.tip
    text += "\n\n"
    tags = article.tags

    for tag in tags:
        text += " #" + tag.name

    await call.message.edit_text(text, reply_markup=mark)


async def go_to_profile(call: types.CallbackQuery):
    await profile_menu_inline(call)


async def start_search(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(start_search_text)
    await state.set_state(SearchState.query.state)


async def search_for_articles(message: types.Message, state: FSMContext):
    query = message.text
    try:
        stored_byte_string = redis_client.get(query)
        tip_list = pickle.loads(stored_byte_string)
        print('found this query in REDIS')
    except TypeError:
        tip_list = tips_crud.search_tips(query)
        byte_string = pickle.dumps(tip_list)
        redis_client.setex(query, 600, byte_string, )
        print('Did not find this query in REDIS')

    if len(tip_list) == 0:
        await message.answer(no_articles_found, reply_markup=profile_kb)
        await state.finish()
        return

    buttons = [InlineKeyboardButton(
        text=tip.header,
        callback_data=show_article_callback.new(str(tip.id))
    )
        for tip in tip_list]


    mark = InlineKeyboardMarkup(row_width=1)
    mark.add(*buttons)
    mark.add(InlineKeyboardButton(text="Назад",
                                  callback_data="В профиль"))
    await state.finish()

    # redis_client.set(query, tip_list)
    await message.answer("Here are articles that match search: ", reply_markup=mark)


async def load_article(call: CallbackQuery, callback_data: dict):
    print(call.data)
    print('Run func load article')
    post_id = callback_data["id"]
    article = tips_crud.get_tip_by_id(post_id)
    text = f"<b>{article.header}</b> \n\n"
    text += article.tip
    text += "\n\n"
    tags = article.tags

    for tag in tags:
        text += " #" + tag.name.strip()
    with suppress(MessageNotModified):
        await call.message.edit_text(text, reply_markup=add_bookmark_go_back(article.id))


async def my_city(call: types.CallbackQuery):
    await call.answer('Раздел "мой город" находится в разработке. Скоро здесь вы сможете найти куда сходить с ребёнком, '
                      'а также новые знакомства!')


def register_profile_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(profile_menu_inline, Text(equals="В профиль"))
    dp.register_callback_query_handler(my_child, Text(equals="Мой ребёнок"))
    dp.register_callback_query_handler(get_my_bookmarks, Text(equals=['< Назад к списку']))
    dp.register_callback_query_handler(get_my_bookmarks, Text(equals=["Сохранённые статьи"]))
    dp.register_callback_query_handler(go_to_profile, Text(equals=["В профиль"]))
    dp.register_callback_query_handler(show_bookmarked_tip, bookmark_link_cb.filter())

    dp.register_callback_query_handler(start_search, Text(equals="Поиск по статьям"))
    dp.register_message_handler(search_for_articles, state=SearchState.query)
    dp.register_callback_query_handler(load_article, show_article_callback.filter())

    dp.register_callback_query_handler(my_city, Text(equals="Мой город"))