import datetime
from contextlib import suppress

from aiogram.utils.exceptions import MessageNotModified
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database.models import Child
from app.database.user_crud import update_user_last_seen
from app.extentions import logger
from app.keyboards.inline.main_kb_inline import main_keyboard_registered
from app.database import user_crud, tips_crud
from app.utils.form_tip_list import form_tip_list

from app.utils.validators import validate_category
from app.keyboards.inline.bookmarks import already_bookmarked_kb, already_bookmarked_keyboard_from_search
from app.keyboards.inline.bookmarks import bookmarks_cb

from app.texts.article_search_texts import category_introduction
from app.texts.basic import child_too_old

from app.utils.validators import calculate_age_in_days, calc_age_range_from_int

from config import CATEGORIES, CATEGORIES_callback



class AgeAndCategory(StatesGroup):
    data = State()


async def show_tips_for_category(call: types.CallbackQuery, state: FSMContext, data: dict|bool = False) -> None:
    """
    This function forms reply markup with all the tips found in given category and sends it as a reply_markup
    """
    user_child: Child = user_crud.get_user_child(call.from_user.id)[0]
    age_range: dict = calc_age_range_from_int(calculate_age_in_days(user_child))
    logger.info(f"User {call.from_user.id} child suits age_range: {age_range}")

    if 'error' in age_range:
        await call.message.edit_text(child_too_old)
        return

    query_data = {
        'category': call.data,
        'from_day': age_range['start'],
        'until_day': age_range['end']
    }

    await state.set_state(AgeAndCategory.data.state)
    await state.update_data(data=query_data)

    reply_mark = form_tip_list(query_data)

    reply_mark.add(InlineKeyboardButton(
        text="В меню",
        callback_data='В меню'
    ))

    await call.message.edit_text(category_introduction, reply_markup=reply_mark)

    logger.info(f"User {call.from_user.id} has chosen category {query_data['category']}.")
    update_user_last_seen(call.from_user.id)


async def back_to_articles(call: types.CallbackQuery, state: FSMContext):
    print('got this callback at: ')
    print(datetime.datetime.now())
    data = await state.get_data()

    await show_tips_for_category(call, state=state, data=data)


async def to_main_menu(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Возвращаемся в главное меню", reply_markup=main_keyboard_registered(call.from_user.id))

async def save_to_bookmarks(call: types.CallbackQuery, callback_data: dict):

    with suppress(MessageNotModified):
        if callback_data['place'] == 'search':
            reply_markup = already_bookmarked_keyboard_from_search
        elif callback_data['place'] == 'categories':
            reply_markup = already_bookmarked_kb

        user_id = call.message.chat.id
        article_id = int(callback_data['tip_id'])
        user_crud.add_bookmark(user_id, article_id)
        await call.answer('Добавлено в сохранённые. Вы можете найти эту статью быстрее через меню профиля если вы его открыли.')
        await call.message.edit_reply_markup(reply_markup)

    logger.info(f"User {call.from_user.id} saved tip with ID: {article_id}")

async def already_saved(call: types.CallbackQuery, callback_data: dict):
    print(callback_data)
    await call.answer('Статья уже была сохранена ранее, вы можете найти её в профиле. Удалить из сохранённых можно там же')

def register_articles_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(show_tips_for_category, Text(equals=CATEGORIES_callback))
    dp.register_callback_query_handler(already_saved, bookmarks_cb.filter(tip_id='0'), state="*")
    dp.register_callback_query_handler(save_to_bookmarks, bookmarks_cb.filter(), state="*")
    # dp.register_callback_query_handler(back_to_articles, Text(equals="Назад"), state=AgeAndCategory.data)
    dp.register_callback_query_handler(to_main_menu, Text(equals="В меню"), state='*')
