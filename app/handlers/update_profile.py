from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.utils.validators import validate_city
from app.keyboards.inline.update_info import cb, edit_info_keyboard
from app.database.user_crud import get_user_by_id, update_user

from app.keyboards.inline.profile_kb_inline import profile_kb

class CityInfo(StatesGroup):
    city = State()


async def update_info(call: types.CallbackQuery):
    await call.message.edit_text("Выберите данные, которые вы хотели бы изменить",
                         reply_markup=edit_info_keyboard())


async def update_city(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.set_state(CityInfo.city.state)
    await call.message.edit_text("Пожалуйста, введите новый город")


async def new_city_name(message: types.Message, state: FSMContext):
    # TODO: Add proper validation
    # Validate city name
    user_id = message.from_user.id
    # city = validate_city(message.text)

    # Get user Id, find him in db and update city
    # if city:
    update_user(user_id, "city", message.text)
    await message.answer(f"Ваш город изменён на: {message.text}. Бот будет базировать рекомендации исходя из этой информации",
                         reply_markup=profile_kb)
    await state.finish()
    # else:
    #     await message.answer(f"I cannot find given city")


def register_update_info_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(update_info, Text(equals="Обновить данные"))
    dp.register_callback_query_handler(update_city, cb.filter())
    dp.register_message_handler(new_city_name, state=CityInfo.city)