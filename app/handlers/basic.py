import datetime

from aiogram import types
from aiogram import Dispatcher

from aiogram.dispatcher.filters import Text
from app.keyboards.main_keyboards import categories_keyboard, initial_keyboard
from app.keyboards.age_select_keyboard import ages_keyboard
from app.database.user_crud import create_user


async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    created_at = datetime.datetime.now()
    user, comment = create_user(user_id, created_at)

    if comment == 'exists':
        reply_kb = categories_keyboard()
        text = """Well hello again, you sick fuck"""
        await message.answer(text, reply_markup=reply_kb)
        return

    reply_kb = initial_keyboard()

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
    await message.answer(text, reply_markup=reply_kb)


async def show_ages_keyboard(message: types.Message):
    await message.answer("Please choose suitable age", reply_markup=ages_keyboard())



def register_basic_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(show_ages_keyboard, Text(equals='Choose age'))