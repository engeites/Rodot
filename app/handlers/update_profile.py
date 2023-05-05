from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.keyboards.inline.update_info import cb, edit_info_keyboard
from app.database import user_crud

from app.keyboards.inline.profile_kb_inline import profile_kb
from app.utils.validators import validate_date


class CityInfo(StatesGroup):
    city = State()

class BabyInfo(StatesGroup):
    new_birthdate = State()


async def update_info(call: types.CallbackQuery):
    await call.message.edit_text("Выберите данные, которые вы хотели бы изменить",
                         reply_markup=edit_info_keyboard())


async def update_city(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.set_state(CityInfo.city.state)
    await call.message.edit_text("Пожалуйста, введите новый город")


async def get_new_city_name(message: types.Message, state: FSMContext):
    # TODO: Add proper validation
    user_id = message.from_user.id
    user_crud.update_user(user_id, "city", message.text)
    await message.answer(f"Ваш город изменён на: {message.text}.",
                         reply_markup=profile_kb)
    await state.finish()


async def update_child_birthdate(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.set_state(BabyInfo.new_birthdate.state)
    await call.message.edit_text("Пожалуйста, введите новую дату рождения в формате дд.мм.гг (например, 01.01.2020)")


async def get_new_birthdate(message: types.Message, state: FSMContext):
    user_input = message.text
    birthdate = validate_date(user_input)

    if not birthdate:
        await message.answer("Не смог распознать введённый формат даты. Попробуйте ещё раз")
        return

    user_id: int = message.from_user.id
    user_crud.update_users_child_birthdate(user_id, birthdate)

    await message.answer(f"Дата рождения изменена на: {message.text}.",
                         reply_markup=profile_kb)
    await state.finish()

def register_update_info_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(update_info, Text(equals="🔄 Обновить данные"))

    # Handlers for updating user city
    dp.register_callback_query_handler(update_city, cb.filter(field="city"))
    dp.register_message_handler(get_new_city_name, state=CityInfo.city)

    # Handlers for updating user child birthdate
    dp.register_callback_query_handler(update_child_birthdate, cb.filter(field="birthdate"))
    dp.register_message_handler(get_new_birthdate, state=BabyInfo.new_birthdate)