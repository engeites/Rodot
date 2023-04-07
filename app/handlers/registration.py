from asyncio import sleep
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery

from app.database.daily_tips import send_daily_tip_to_user
from app.database.user_crud import update_user_last_seen
# from app.keyboards.main_keyboards import main_keyboard_registered
from app.keyboards.inline.main_kb_inline import main_kb_unregistered, main_keyboard_registered
# from app.texts.registration_texts import start_registration, date_input_failed, input_sex, sex_input_failed, input_city
from app.texts import registration_texts

from app.database import user_crud
from app.utils.texts_handling import handle_daily_article
from app.utils.validators import validate_date

from app.keyboards.inline import child_sex
from config import SEND_DAILY_ARTICLE_AFTER_REG, CITIES

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


cancel_kb = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Отмена', callback_data='Отмена'))

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
    if given_city.lower() not in CITIES:
        return False
    return given_city


async def profile_start(call: types.CallbackQuery, state: FSMContext):
    """
    This function is called when "Заполнить профиль" button is pressed
    :param call:
    :param state:
    :return: None
    """
    child_exists = user_crud.get_user_child(call.from_user.id)

    update_user_last_seen(call.from_user.id)


    if not child_exists:
        print(child_exists) # (datetime.datetime(2023, 3, 16, 0, 0), 'male')
        await call.message.edit_text(registration_texts.start_registration, reply_markup=cancel_kb)
        await state.set_state(ProfileInfo.birth_date.state)

    else:
        await call.message.edit_text(registration_texts.already_have_child, reply_markup=main_keyboard_registered(call.from_user.id))


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


async def city_set(message: types.Message, state: FSMContext):
    given_city = message.text
    # city = validate_city(given_city)
    if not given_city:
        return

    user_data = await state.get_data()
    success = user_crud.add_child(
        message.from_user.id,
        user_data['birth_date'],
        user_data['sex'],
    )

    await message.answer(registration_texts.reg_finished, reply_markup=main_keyboard_registered(message.from_user.id))
    await state.finish()

    # wait for some time and send article after some time, because articles are sent once per day and user may register after that time.
    await sleep(SEND_DAILY_ARTICLE_AFTER_REG)

    todays_tip = send_daily_tip_to_user(message.from_user.id)
    if not todays_tip:
        pass
    else:
        article_to_send: dict = handle_daily_article(send_daily_tip_to_user(message.from_user.id))

        message_text = f"""
        <b>{article_to_send['header']}</b>
    
        {article_to_send['body']}
        """

        if article_to_send['media']:
            await message.answer_photo(article_to_send['media'], caption=message_text)
        else:
            await message.answer(message_text)


async def cancel_questionnaire(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text(registration_texts.cancel_registration, reply_markup=main_kb_unregistered)


def register_registry_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(cancel_questionnaire,  Text(equals='Отмена'), state='*')
    dp.register_callback_query_handler(profile_start, Text(equals="📖 Заполнить профиль"), state='*')
    dp.register_message_handler(birthday_set, state=ProfileInfo.birth_date)
    dp.register_callback_query_handler(sex_set, child_sex.cb.filter(), state=ProfileInfo.sex)
    dp.register_message_handler(city_set, state=ProfileInfo.city)

