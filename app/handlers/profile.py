import aiogram
from aiogram import types
from aiogram.dispatcher.filters import Text

from app.keyboards.inline.bookmarks import bookmark_link_cb, all_bookmarks_keyboard

from app.database import user_crud, tips_crud


async def my_child(message: types.Message):
    user = user_crud.get_user_by_tg_id(message.from_user.id)
    child = user.children

    await message.answer(child)


async def get_my_bookmarks(message: types.Message):
    user_id = message.from_user.id
    await message.answer("Here are your saved bookmarks", reply_markup=all_bookmarks_keyboard(user_id))


async def show_bookmarked_tip(call: types.CallbackQuery, callback_data: dict):
    article = tips_crud.get_tip_by_id(callback_data['tip_id'])
    text = article.header
    text += "\n\n"
    text += article.tip
    text += "\n\n"
    tags = article.tags

    for tag in tags:
        text += " #" + tag.name

    await call.message.answer(text)

def register_profile_handlers(dp: aiogram.Dispatcher):
    dp.register_message_handler(my_child, Text(equals="My Child"))
    dp.register_message_handler(get_my_bookmarks, Text(equals="My Saved Articles"))
    dp.register_callback_query_handler(show_bookmarked_tip, bookmark_link_cb.filter())