from contextlib import suppress

import config

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import MessageNotModified

from app.database.models import ParentingTip
from app.keyboards.inline.bookmarks import bookmark_link_cb, all_bookmarks_keyboard
from app.keyboards.inline.profile_kb_inline import profile_kb
from app.keyboards.inline.bookmarks import add_bookmark_go_back

from app.texts.profile_texts import start_search_text, no_articles_found, list_of_found_articles, ask_new_question

from app.database import user_crud, tips_crud
from app.utils.message_renderers import MyChildMessageRenderer, TipRenderer
from app.texts import bookmark_texts, profile_texts

from app.extentions import logger

show_article_callback = CallbackData('show_article', 'id')

class SearchState(StatesGroup):
    query = State()


class AskState(StatesGroup):
    question = State()

async def profile_menu_inline(call: types.CallbackQuery):
    logger.info(f"User {call.from_user.id} opened profile menu")
    await call.message.edit_text(profile_texts.profile_introduction,
        reply_markup=profile_kb)


async def my_child(call: types.CallbackQuery):
    user = user_crud.get_user_by_tg_id(call.from_user.id)

    formatter = MyChildMessageRenderer(user)
    message_text = formatter.form_final_message()

    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(
        text="⬆️ В профиль",
        callback_data='В профиль'
    ))
    logger.info(f'User {call.from_user.id} checked "My child"')
    await call.message.edit_text(message_text, reply_markup=mark)


async def get_my_bookmarks(call: types.CallbackQuery):

    user_id = call.from_user.id
    keyboard_with_bookmarks = all_bookmarks_keyboard(user_id)
    if not keyboard_with_bookmarks:
        await call.message.answer(bookmark_texts.no_bookmarks_found)
        logger.info(f"User {call.from_user.id} checked bookmarks before he added any")
        return

    logger.info(f"User {call.from_user.id} checked his bookmarks")
    await call.message.edit_text(list_of_found_articles, reply_markup=keyboard_with_bookmarks)


async def show_bookmarked_tip(call: types.CallbackQuery, callback_data: dict):

    mark = InlineKeyboardMarkup(row_width=1)

    mark.add(InlineKeyboardButton(
        text="< Назад к списку",
        callback_data='< Назад к списку'
    ))

    tip: ParentingTip = tips_crud.get_tip_by_id(callback_data['tip_id'])

    formatter = TipRenderer(tip)
    message_text = formatter.form_final_text()
    logger.info(f"User {call.from_user.id} opened previously added tip: {tip.header}")
    await call.message.edit_text(message_text, reply_markup=mark)


async def go_to_profile(call: types.CallbackQuery):
    await profile_menu_inline(call)


async def start_search(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(start_search_text)
    await state.set_state(SearchState.query.state)


async def search_for_articles(message: types.Message, state: FSMContext):
    query = message.text
    tip_list = tips_crud.search_tips_by_query(query)

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
    logger.info(f"User {message.from_user.id} searched next query: {query}")
    await message.answer("Вот что удалось найти по вашему запросу: ", reply_markup=mark)


async def render_article(call: CallbackQuery, callback_data: dict):
    post_id = callback_data["id"]
    tip: ParentingTip = tips_crud.get_tip_by_id(post_id)

    renderer = TipRenderer(tip)
    message_text = renderer.form_final_text()

    logger.info(f"User {call.from_user.id} opened a tip: {tip.header}")

    with suppress(MessageNotModified):
        await call.message.edit_text(message_text, reply_markup=add_bookmark_go_back(tip.id))



async def ask_others(call: types.CallbackQuery, state: FSMContext):
    logger.info(f"User {call.from_user.id} wants to ask community a question")
    logger.info(call.message.chat.id)
    await state.set_state(AskState.question.state)
    mark =  InlineKeyboardMarkup(row_width=1)
    mark.add(InlineKeyboardButton(
        text="Отмена",
        callback_data='cancel_question')
    )
    await call.message.edit_text(ask_new_question, reply_markup=mark)


async def send_question_to_admin(message: types.Message, state: FSMContext):
    logger.info(message)
    await message.forward(config.ADMIN_CHAT)
    await message.answer("Ваш вопрос добавлен в очередь. Администратор опубликует его после обработки",
                         reply_markup=profile_kb)
    await state.finish()

async def cancel_question(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Вопрос отменён", reply_markup=profile_kb)


async def day_by_day(call: types.CallbackQuery):
    logger.info(f"User {call.from_user.id} tried to open 'Day by day' functionality")

    await call.answer('Подписка уже оформлена автоматически')


def register_profile_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(profile_menu_inline, Text(equals="В профиль"))
    dp.register_callback_query_handler(my_child, Text(equals="👼🏻 Мой ребёнок"))
    dp.register_callback_query_handler(get_my_bookmarks, Text(equals=['< Назад к списку']))
    dp.register_callback_query_handler(get_my_bookmarks, Text(equals=["📗 Сохранённые статьи"]))
    dp.register_callback_query_handler(day_by_day, Text(equals=["🤳🏼 День за днём"]))
    dp.register_callback_query_handler(show_bookmarked_tip, bookmark_link_cb.filter())

    dp.register_callback_query_handler(start_search, Text(equals="🔎 Поиск по статьям"))
    dp.register_message_handler(search_for_articles, state=SearchState.query)
    dp.register_callback_query_handler(render_article, show_article_callback.filter())

    dp.register_callback_query_handler(ask_others, Text(equals="🆘 Задать вопрос"), state="*")
    dp.register_message_handler(send_question_to_admin, state=AskState.question, content_types=['photo', 'text'])
    dp.register_callback_query_handler(cancel_question, Text(equals="cancel_question"), state=AskState.question)