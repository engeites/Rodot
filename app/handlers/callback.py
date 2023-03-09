from aiogram.types import CallbackQuery
from aiogram.utils.callback_data import CallbackData


callback_data = CallbackData('articles', 'id')

async def button_callback_handler(callback: CallbackQuery, callback_data: dict):
    button_id = callback_data.get('id')
    await callback.answer(button_id)

