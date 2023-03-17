from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from app.keyboards.main_keyboards import main_keyboard_registered
from app.keyboards.profile import profile_keyboard

from app.database.tips_crud import get_all_tips, get_tip_by_id, get_tips_by_multiple_tags
from app.database import user_crud

from app.keyboards.inline.bookmarks import add_bookmark_keyboard
from app.keyboards.inline.bookmarks import cb

from app.utils.form_newborn_contents import newborn_section_introduction
from app.utils.validators import calculate_age_in_days, calc_age_range_from_int

callback_data = CallbackData('articles', 'id')

async def health_and_security_tips(message: types.Message):
    mark = InlineKeyboardMarkup()

    tag_list = ['новорожденные', "здоровье"]

    # tips = get_all_tips()
    user_child = user_crud.get_user_child(message.from_user.id)
    child_age_in_days: int = calculate_age_in_days(user_child[0])

    age_range: dict = calc_age_range_from_int(child_age_in_days)
    # Here I only have child's birthday
    #   It seems like no, I store kid's age in days for some reason. Need to remake that and store birthday.
    #   I will convert birthday to a number (age in days)
    #   And then need to get the age range, like if age in days = 5, then age range = 1:30, if age = 189 then age range = 180:270

    tips = get_tips_by_multiple_tags(tag_list, age_range['start'], age_range['end'])
    for tip in tips:
        mark.add(InlineKeyboardButton(
            text=tip.header,
            callback_data=callback_data.new(str(tip.id))
        ))

    await message.answer(newborn_section_introduction(), reply_markup=mark)


async def callbacks(call: types.CallbackQuery, callback_data: dict):
    post_id = callback_data["id"]
    article = get_tip_by_id(post_id)
    text = article.header
    text += "\n\n"
    text += article.tip
    text += "\n\n"
    tags = article.tags

    for tag in tags:
        text += " #" + tag.name.strip()

    await call.message.answer(text, reply_markup=add_bookmark_keyboard(article.id))


async def save_to_bookmarks(call: types.CallbackQuery, callback_data: dict):
    user_id = call.message.chat.id
    article_id = int(callback_data['tip_id'])
    user_crud.add_bookmark(user_id, article_id)
    await call.message.answer("Successfully added new bookmark")


def register_articles_handlers(dp: Dispatcher):
    dp.register_message_handler(health_and_security_tips, Text(equals="Здоровье и гигиена"))
    dp.register_callback_query_handler(callbacks, callback_data.filter())
    dp.register_callback_query_handler(save_to_bookmarks, cb.filter())