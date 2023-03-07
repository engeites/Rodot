from datetime import datetime
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup


class ProfileUpdate():
    def __init__(self, birth_date, sex, city):
        self.birth_date = birth_date
        self.sex = sex
        self.city = city


class ProfileInfo(StatesGroup):
    birth_date = State()
    sex = State()
    city = State()


def validate_date(given_date: str) -> datetime:
    return datetime.now()


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
    await message.answer("Please enter your child's day of birth in format: day/month/year")
    await state.set_state(ProfileInfo.birth_date.state)


async def birthday_set(message: types.Message, state: FSMContext):
    given_date = message.text
    datetime_date = validate_date(given_date)
    if not datetime_date:
        return
    await state.update_data(birth_date=datetime_date)
    await state.set_state(ProfileInfo.sex.state)
    await message.answer("Please input child's sex")

async def sex_set(message: types.Message, state: FSMContext):
    given_sex = message.text
    final_sex = validate_sex(given_sex)
    if not final_sex:
        return
    await state.update_data(sex=final_sex)
    await state.set_state(ProfileInfo.city.state)
    await message.answer("Please input the name of your city")


async def city_set(message: types.Message, state: FSMContext):
    given_city = message.text
    city = validate_city(given_city)
    if not city:
        return

    user_data = await state.get_data()
    update = ProfileUpdate(
        user_data['birth_date'],
        user_data['sex'],
        message.text
    )

    await message.answer(f"You have updated info: day of birth: {update.birth_date}, sex: {update.sex},"
                         f"city: {update.city}")
    await state.finish()


def register_profile_handlers(dp: Dispatcher):
    dp.register_message_handler(profile_start, commands=['update'], state='*')
    dp.register_message_handler(birthday_set, state=ProfileInfo.birth_date)
    dp.register_message_handler(sex_set, state=ProfileInfo.sex)
    dp.register_message_handler(city_set, state=ProfileInfo.city)

