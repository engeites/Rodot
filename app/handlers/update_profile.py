from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.utils.validators import validate_city
from app.keyboards.inline.update_info import cb, edit_info_keyboard
from app.database.user_crud import get_user_by_id, update_user

class CityInfo(StatesGroup):
    city = State()


async def update_info(message: types.Message):
    # user = get_user_by_id(1)
    await message.answer("Select field that you would like to update?",
                         reply_markup=edit_info_keyboard())


async def update_city(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.set_state(CityInfo.city.state)
    await call.message.answer("Please input city name")


async def new_city_name(message: types.Message, state: FSMContext):
    # Validate city name
    user_id = message.from_user.id
    city = validate_city(message.text)

    # Get user Id, find him in db and update city
    if city:
        update_user(user_id, "city", city)
        await message.answer(f"You have set your city as: {message.text}")
        await state.finish()
    else:
        await message.answer(f"I cannot find given city")
def register_info_handlers(dp: Dispatcher):
    dp.register_message_handler(update_info, Text(equals="Обновить данные"))
    dp.register_callback_query_handler(update_city, cb.filter())
    dp.register_message_handler(new_city_name, state=CityInfo.city)