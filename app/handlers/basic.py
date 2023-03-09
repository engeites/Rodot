import datetime

from aiogram import types
from aiogram import Dispatcher
from app.keyboards.main_keyboard import create_main_keyboard
from app.database.user_crud import create_user


async def send_welcome(message: types.Message):
    created_at = datetime.datetime.now()
    user_id = message.from_user.id
    user = create_user(user_id, created_at)

    text = """
    Hello and welcome to the Parenting Tips bot! 

I'm here to help you navigate the challenges of parenting and provide you with valuable information and advice for your child's development. 

To get started, please select a category from the menu below:
- Newborn Care
- Sleeping Tips
- Feeding Advice
- Developmental Activities
- And more!

You can also search for articles by typing a keyword or topic in the search bar. 

Thank you for using Parenting Tips bot, and happy parenting! 
"""
    await message.answer(text, reply_markup=create_main_keyboard())

def register_basic_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])