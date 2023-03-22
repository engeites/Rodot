from contextlib import suppress

from aiogram.utils.exceptions import MessageNotModified
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from app.keyboards.main_keyboards import main_keyboard_registered
from app.keyboards.profile import profile_keyboard

from app.database.tips_crud import get_all_tips, get_tip_by_id, get_tips_by_multiple_tags
from app.database import user_crud

from app.keyboards.inline.bookmarks import add_bookmark_keyboard, already_bookmarked_kb
from app.keyboards.inline.bookmarks import cb

from app.utils.form_newborn_contents import newborn_section_introduction
from app.utils.validators import calculate_age_in_days, calc_age_range_from_int

from app.config import CATEGORIES

callback_data = CallbackData('articles', 'id')

async def show_tips_for_category(call: types.CallbackQuery):
    mark = InlineKeyboardMarkup()

    tag_list = [call.data]

    # tips = get_all_tips()
    user_child = user_crud.get_user_child(call.from_user.id)
    child_age_in_days: int = calculate_age_in_days(user_child[0])
    print(user_child)
    print(child_age_in_days)
    age_range: dict = calc_age_range_from_int(child_age_in_days)
    print(age_range)
    tips = get_tips_by_multiple_tags(tag_list, age_range['start'], age_range['end'])
    for tip in tips:
        mark.add(InlineKeyboardButton(
            text=tip.header,
            callback_data=callback_data.new(str(tip.id))
        ))

    await call.message.edit_text(newborn_section_introduction(), reply_markup=mark)



async def save_to_bookmarks(call: types.CallbackQuery, callback_data: dict):
    with suppress(MessageNotModified):
        print(callback_data)
        user_id = call.message.chat.id
        article_id = int(callback_data['tip_id'])
        user_crud.add_bookmark(user_id, article_id)
        await call.answer('Добавлено в сохранённые. Вы можете найти эту статью быстрее через меню профиля если вы его открыли.')
        await call.message.edit_reply_markup(already_bookmarked_kb)


async def already_saved(call: types.CallbackQuery, callback_data: dict):
    print(callback_data)
    await call.answer('Статья уже была сохранена ранее, вы можете найти её в профиле. Удалить из сохранённых можно там же')

def register_articles_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(show_tips_for_category, Text(equals=CATEGORIES))
    dp.register_callback_query_handler(already_saved, cb.filter(tip_id='0'), state="*")
    dp.register_callback_query_handler(save_to_bookmarks, cb.filter(), state="*")
