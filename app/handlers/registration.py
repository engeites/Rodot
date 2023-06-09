from asyncio import sleep
from aiogram import Dispatcher, types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import CallbackQuery

from app.database.daily_tips import find_daily_tip_for_user
from app.extentions import logger
from app.keyboards.inline.day_to_day_sub import confirm_subscription_kb
# from app.keyboards.main_keyboards import main_keyboard_registered
from app.keyboards.inline.main_kb_inline import initial_kb, main_keyboard_registered
# from app.texts.registration_texts import start_registration, date_input_failed, input_sex, sex_input_failed, input_city
from app.texts import registration_texts

from app.database import user_crud
from app.texts.registration_texts import subscribed_to_day_to_day, canceled_subscription
from app.utils.texts_handling import handle_daily_article
from app.utils.validators import validate_date, add_days_to_today_utc

from app.keyboards.inline import child_sex
from config import SEND_DAILY_ARTICLE_AFTER_REG, CITIES, BASIC_DAY_TO_DAY_SUBSCRIPTION_LENGTH

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


cancel_kb = InlineKeyboardMarkup().add(InlineKeyboardButton(text='Отмена', callback_data='Отмена'))

class DayToDay(StatesGroup):
    subscribe = State()

class ProfileInfo(StatesGroup):
    birth_date = State()
    sex = State()
    city = State()


def validate_sex(given_sex: str) -> str | bool:
    options = ['male', 'female', 'unknown']
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

    user_crud.update_user_last_seen(call.from_user.id)


    if not child_exists:
        logger.info(f"Starting process of registering a child for user {call.from_user.id}")
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
    logger.info(f"Added new child for user {message.from_user.id}. Registration process finished successfully.")

    success = user_crud.update_user_city(message.from_user.id, given_city)
    logger.info(f"Updated city for user {message.from_user.id}. New city: {given_city}.")

    await state.finish()

    await message.answer(registration_texts.reg_finished, reply_markup=confirm_subscription_kb)
    # TODO: Here need to add additional dialog: Day by day subscription is now free, do you want to activate it?
    # wait for some time and send article after some time, because articles are sent once per day and user may register after that time.

    await DayToDay.subscribe.set()

async def subscription_confirmed(call: types.CallbackQuery, state: FSMContext):

    await call.message.edit_text(subscribed_to_day_to_day,
                                 reply_markup=main_keyboard_registered(call.from_user.id))

    await state.finish()


    user_id: int = call.from_user.id

    # Update user model
    subscription_end = add_days_to_today_utc(BASIC_DAY_TO_DAY_SUBSCRIPTION_LENGTH)
    logger.info(f"User {call.from_user.id} subscribed to Day-to-day service. Subscription end at: {subscription_end}")
    user_crud.update_user(user_id, 'subscription_end', subscription_end)

    await sleep(SEND_DAILY_ARTICLE_AFTER_REG)
    # Find a tip to send
    todays_tip = find_daily_tip_for_user(user_id)
    if not todays_tip:
        return

    article_to_send: dict = handle_daily_article(find_daily_tip_for_user(user_id))

    message_text = f"""
    <b>{article_to_send['header']}</b>

    {article_to_send['body']}
    """

    if article_to_send['media']:
        await call.message.answer_photo(article_to_send['media'], caption=message_text)
        logger.info(f"Sent daily article with name: {article_to_send['header']} to user {user_id}")
    else:
        await call.message.answer(message_text)


async def subscription_cancelled(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text(canceled_subscription,
                                 reply_markup=main_keyboard_registered(call.from_user.id))
    await state.finish()


async def input_error(message: types.Message, state: FSMContext):
    await message.answer(registration_texts.sex_input_failed)


async def cancel_questionnaire(call: CallbackQuery, state: FSMContext):
    await state.finish()
    logger.info(f"Registration process cancelled for user {call.from_user.id}")
    await call.message.edit_text(registration_texts.cancel_registration, reply_markup=initial_kb)


def register_registry_handlers(dp: Dispatcher):
    # Handlers for registration process
    dp.register_callback_query_handler(cancel_questionnaire,  Text(equals='Отмена'), state='*')
    dp.register_callback_query_handler(profile_start, Text(equals="Заполнить профиль"), state='*')
    dp.register_message_handler(birthday_set, state=ProfileInfo.birth_date)
    dp.register_callback_query_handler(sex_set, child_sex.cb.filter(), state=ProfileInfo.sex)
    dp.register_message_handler(city_set, state=ProfileInfo.city)
    dp.register_message_handler(input_error, state=[ProfileInfo.sex])

    # Handlers for day-to-day subscription
    dp.register_callback_query_handler(subscription_confirmed, Text(equals="confirm_subscription"), state=DayToDay.subscribe)
    dp.register_callback_query_handler(subscription_cancelled, Text(equals="cancel_subscription"), state=DayToDay.subscribe)