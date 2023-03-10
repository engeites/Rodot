import aiogram
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from app.keyboards.main_keyboards import categories_keyboard
from app.keyboards.profile import profile_keyboard
from app.database.tips_crud import get_all_tips, get_tip_by_id
from app.database import user_crud

from app.utils.form_newborn_contents import newborn_section_introduction


async def my_child(message: types.Message):
    user = user_crud.get_user_by_tg_id(message.from_user.id)
    child = user.children

    print(child)


def register_profile_handlers(dp: aiogram.Dispatcher):
    dp.register_message_handler(my_child, Text(equals="My child"))