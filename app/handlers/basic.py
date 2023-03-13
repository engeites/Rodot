import datetime

from aiogram import types
from aiogram import Dispatcher

from aiogram.dispatcher.filters import Text
from app.keyboards.main_keyboards import main_keyboard, initial_keyboard
from app.keyboards.article_filtering_keyboards import ages_keyboard, categories_keyboard
from app.database.user_crud import create_user

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class AgeAndTheme(StatesGroup):
    age = State()
    category = State()


async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    created_at = datetime.datetime.now()
    user, comment = create_user(user_id, created_at)

    if comment == 'exists':
        reply_kb = main_keyboard()
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



async def get_age(message: types.Message, state: FSMContext):
    given_age = message.text
    # TODO: Validate if message was from the given keyboard, CRITICAL

    await state.update_data(age=given_age)
    await message.answer("Choose a theme where you need advice", reply_markup=categories_keyboard())
    await state.set_state(AgeAndTheme.category.state)

async def get_category(message: types.Message, state:FSMContext):
    given_category = message.text
    # TODO: validate categories too, CRITICAL

    await state.update_data(category=given_category)

    search_filters = await state.get_data()

    # Search for article that suits the given age and category
    # Return list of articles in inline keyboard
    await message.answer(f"You have selected: {search_filters['age']}, {search_filters['category']}")
    await state.finish()

options = [
    "Health and Security",
    "Feeding",
    "Sleeping and Schedule",
    "Developmental Activities",
    "Books and Toys",
    "Outdated Advice"
]


async def go_to_main(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Opening main menu", reply_markup=main_keyboard())

async def show_ages_keyboard(message: types.Message, state: FSMContext):
    await state.set_state(AgeAndTheme.age.state)
    await message.answer("Please choose suitable age", reply_markup=ages_keyboard())


def register_basic_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(show_ages_keyboard, Text(equals='Choose Age'), state="*")
    dp.register_message_handler(get_age, state=AgeAndTheme.age)
    dp.register_message_handler(get_category, Text(equals=options), state=AgeAndTheme.category)
    dp.register_message_handler(go_to_main, state="*")