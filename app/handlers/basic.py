import datetime

from aiogram import types
from aiogram import Dispatcher
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from aiogram.dispatcher.filters import Text
from app.keyboards.main_keyboards import main_keyboard_registered, main_keyboard_unregistered, initial_keyboard
from app.keyboards.article_filtering_keyboards import categories_keyboard#, ages_keyboard
from app.keyboards.inline.ages import ages_keyboard, cb
from app.database import user_crud
from app.database import tips_crud

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.texts.main_menu import main_menu_unregistered, main_menu_registered
from app.texts.basic import welcome, our_philosophy
from app.texts.article_search_texts import category_not_found

from app.config import CATEGORIES

callback_data = CallbackData('articles', 'id')

class AgeAndTheme(StatesGroup):
    from_day = State()
    until_day = State()
    category = State()

#
# options = [
#     "Здоровье и гигиена",
#     "Кормление",
#     "Сон и режим",
#     "Игры и развитие",
#     "Книги и игрушки",
#     "Вредные советы"
# ]


async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    created_at = datetime.datetime.now()
    user, comment = user_crud.create_user(user_id, created_at)

    if comment == 'exists':
        reply_kb = main_keyboard_registered()
        text = """Well hello again, you sick fuck"""
        await message.answer(welcome, reply_markup=initial_keyboard())
        return

    reply_kb = initial_keyboard()
    await message.answer(welcome, reply_markup=reply_kb)


async def show_ages_keyboard(message: types.Message, state: FSMContext):
    await state.set_state(AgeAndTheme.from_day.state)
    await message.answer("Please choose suitable age", reply_markup=ages_keyboard())


async def get_age(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    start_age = callback_data['from_day']
    end_age = callback_data['until_day']
    # TODO: Validate if message was from the given keyboard, CRITICAL
    await state.update_data(from_day=start_age, until_day=end_age)
    await call.message.answer("Choose a theme where you need advice", reply_markup=categories_keyboard())
    await state.set_state(AgeAndTheme.category.state)
#
# async def get_age(message: types.Message, state: FSMContext):
#     given_age = message.text
#
#     await state.update_data(age=given_age)
#     await message.answer("Choose a theme where you need advice", reply_markup=categories_keyboard())
#     await state.set_state(AgeAndTheme.category.state)


async def get_category(message: types.Message, state:FSMContext):
    given_category = message.text
    if given_category not in CATEGORIES:
        await message.answer(category_not_found, reply_markup=categories_keyboard())
        return

    await state.update_data(category=given_category)
    state_data = await state.get_data()

    # Search for article that suits the given age and category
    tips = tips_crud.get_tips_by_multiple_tags([state_data['category']], state_data['from_day'], state_data['until_day'])


    mark = InlineKeyboardMarkup()

    for tip in tips:
        mark.add(InlineKeyboardButton(
            text=tip.header,
            callback_data=callback_data.new(str(tip.id))
        ))
    # Return list of articles in inline keyboard
    await message.answer(f"По выбранным фильтрам есть следующие статьи", reply_markup=mark)
    await state.finish()


async def go_to_main(message: types.Message, state: FSMContext):
    await state.finish()
    user_registered = user_crud.check_if_user_passed_reg(message.from_user.id)

    if user_registered:
        await message.answer(main_menu_registered, reply_markup=main_keyboard_registered())
    else:
        await message.answer(main_menu_unregistered, reply_markup=main_keyboard_unregistered())


# async def show_ages_keyboard(message: types.Message, state: FSMContext):
#     await state.set_state(AgeAndTheme.age.state)
#     await message.answer("Please choose suitable age", reply_markup=ages_keyboard())
#

async def send_our_philosophy(message: types.Message):
    await message.answer(our_philosophy, reply_markup=initial_keyboard())

async def void_messages(message: types.Message):
    print("Got this message that does not suit other handlers: ")
    print(message.text)
    await message.answer("на " + message.text + " у меня нет ответа")


def register_basic_handlers(dp: Dispatcher):
    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(show_ages_keyboard, Text(equals='Выбрать возраст'), state="*")
    dp.register_callback_query_handler(get_age, cb.filter(), state=AgeAndTheme.from_day)
    dp.register_message_handler(get_category, Text(equals=CATEGORIES), state=AgeAndTheme.category)
    dp.register_message_handler(send_our_philosophy, Text(equals="Наша философия"))

    dp.register_message_handler(go_to_main, Text(equals="На главную"), state="*")
    dp.register_message_handler(go_to_main, commands=['cancel'], state="*")
    dp.register_message_handler(void_messages)