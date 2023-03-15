from datetime import datetime
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.keyboards.main_keyboards import main_keyboard_registered

# from app.texts.registration_texts import start_registration, date_input_failed, input_sex, sex_input_failed, input_city
from app.texts import registration_texts

from app.database.user_crud import add_child
from app.utils.validators import validate_date

from app.keyboards.inline import child_sex

class ProfileUpdate():
    def __init__(self, birth_date, sex, city):
        self.birth_date = birth_date
        self.sex = sex
        self.city = city


class ProfileInfo(StatesGroup):
    birth_date = State()
    sex = State()
    city = State()


def validate_sex(given_sex: str) -> str | bool:
    options = ['male', 'female']
    if given_sex.lower() in options:
        return given_sex
    return False

def validate_city(given_city: str) -> str | bool:
    options = ["moscow", "saint petersburg", "rostov", "stavropol", "omsk", "tomsk", "pyatigorsk"]
    if given_city.lower() not in options:
        return False
    return given_city


async def profile_start(message: types.Message, state: FSMContext):
    await message.answer(registration_texts.start_registration)
    await state.set_state(ProfileInfo.birth_date.state)


async def birthday_set(message: types.Message, state: FSMContext):
    given_date = message.text
    datetime_date = validate_date(given_date)
    if not datetime_date:
        await message.answer(registration_texts.date_input_failed)
        return
    await state.update_data(birth_date=datetime_date)
    await state.set_state(ProfileInfo.sex.state)
    await message.answer(registration_texts.input_sex, reply_markup=child_sex.set_child_sex())

async def sex_set(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    final_sex = validate_sex(callback_data['sex'])
    if not final_sex:
        await call.message.answer(registration_texts.sex_input_failed, reply_markup=child_sex.set_child_sex())
        return
    await state.update_data(sex=final_sex)
    await state.set_state(ProfileInfo.city.state)
    await call.message.answer(registration_texts.input_city)
#
# async def sex_set(message: types.Message, state: FSMContext):
#     given_sex = message.text
#     final_sex = validate_sex(given_sex)
#     if not final_sex:
#         return
#     await state.update_data(sex=final_sex)
#     await state.set_state(ProfileInfo.city.state)
#     await message.answer("Please input the name of your city. Send /cancel command to cancel the process")


async def city_set(message: types.Message, state: FSMContext):
    given_city = message.text
    # city = validate_city(given_city)
    if not given_city:
        return

    user_data = await state.get_data()
    success = add_child(
        message.from_user.id,
        user_data['birth_date'],
        user_data['sex'],
    )
    if success:
        await message.answer(registration_texts.reg_finished, reply_markup=main_keyboard_registered())
        await state.finish()
    else:
        await message.answer(f"Error occured")


async def cancel_questionnaire(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Cancelled the questionnaire. No information was saved. However, we highly recommend finishing the process"
                         "as it will make your experience with me much easier")



def register_registry_handlers(dp: Dispatcher):
    dp.register_message_handler(profile_start, Text(equals="Заполнить профиль"), state='*')
    dp.register_message_handler(birthday_set, state=ProfileInfo.birth_date)
    dp.register_callback_query_handler(sex_set, child_sex.cb.filter(), state=ProfileInfo.sex)
    dp.register_message_handler(city_set, state=ProfileInfo.city)
    dp.register_message_handler(cancel_questionnaire,  commands=['cancel'], state='*')

