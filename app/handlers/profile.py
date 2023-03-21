from datetime import datetime

from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

import app.database.models
from app.keyboards.inline.bookmarks import bookmark_link_cb, all_bookmarks_keyboard
from app.keyboards.profile import profile_keyboard
from app.keyboards.inline.profile_kb_inline import profile_kb

from app.database import user_crud, tips_crud
from app.utils.validators import calculate_age_in_days
from app.texts import bookmark_texts, profile_texts


async def profile_menu(message: types.Message):
    await message.answer(profile_texts.profile_introduction,
        reply_markup=profile_keyboard()
    )


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

    await call.message.edit_text(text)


async def get_my_bookmarks(message: types.Message):
    user_id = message.from_user.id
    keyboard_with_bookmarks = all_bookmarks_keyboard(user_id)
    if not keyboard_with_bookmarks:
        await message.answer(bookmark_texts.no_bookmarks_found)
        return
    await message.answer("Вот список сохранённых вами статей", reply_markup=keyboard_with_bookmarks)


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

def register_profile_handlers(dp: Dispatcher):
    dp.register_message_handler(profile_menu, Text(equals="В профиль"))
    dp.register_callback_query_handler(profile_menu_inline, Text(equals="В профиль"))
    dp.register_callback_query_handler(my_child, Text(equals="Мой ребёнок"))
    # dp.register_message_handler(my_child, Text(equals="Мой ребёнок"))
    dp.register_message_handler(get_my_bookmarks, Text(equals="Сохранённые статьи"))
    dp.register_callback_query_handler(show_bookmarked_tip, bookmark_link_cb.filter())