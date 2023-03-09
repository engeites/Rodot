from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from aiogram.dispatcher.filters.state import State, StatesGroup

from app.database.user_crud import get_user_by_id


async def update_info(message: types.Message):
    user = get_user_by_id(1)

    await message.answer(user.__dict__)


def register_info_handlers(dp: Dispatcher):
    dp.register_message_handler(update_info, Text(equals="Update my info"))