import asyncio

import aiogram.utils.exceptions
from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from app.database.advice_crud import add_new_advice
from app.database.db_analytics import get_most_viewed_tips
from app.database.models import AdvertisementLog, ParentingTip
from app.database.user_crud import get_active_users, get_user_registration_stats
from app.extentions import logger, ADMINS
from app.keyboards.inline.admin_kb import admin_kb, cancel_kb
from app.keyboards.inline.main_kb_inline import show_categories
from app.utils.message_renderers import TipRenderer
from app.utils.texts_handling import handle_daily_article
from app.utils.time_ranges import get_hours_passed_today
from app.utils.validators import validate_age
from app.database.tips_crud import create_new_article
from app.database.daily_tips_crud import create_daily_tip, get_list_of_daily_tips, delete_daily_tip_by_id, \
    get_daily_tip_by_id
from app.database import db_analytics, ads_crud, tips_crud, user_crud

from app.keyboards.inline.ages import ages_keyboard, get_ages_cb
from app.keyboards.inline.main_kb_inline import main_keyboard_registered
from app.keyboards.inline.bookmarks import admin_statistics_cb, article_actions_keyboard,\
    add_advertisement_cb, edit_tip_cb, delete_tip_cb


# StatesGroup for normal articles
class Article(StatesGroup):
    """
    Represents StatesGroup for normal ParentingTip
    """
    header = State()
    tip = State()
    category = State()
    age_range = State()


class EditArticle(StatesGroup):
    new_text = State()
    confirm = State()


class DeleteArticle(StatesGroup):
    confirm = State()


class Advertisement(StatesGroup):
    """
    Represents StatesGroup for adding Advertisement to tip
    """
    tip_id = State()
    ad_text = State()
    active_period = State()
    confirm = State()
    vendor = State()


class DailyArticle(StatesGroup):
    """
    Represents StatesGroup for daily articles
    """
    header = State()
    body = State()
    age_in_days = State()
    media = State()


class OneTimeMessage(StatesGroup):
    """
    Represents StatesGroup for one-time-message sending
    """
    body = State()
    media = State()
    confirm = State()


# StatesGroup for Short Advice
class Advice(StatesGroup):
    age_range_start = State()
    age_range_end = State()
    advice = State()


# ------Callback data factories for this module ---------
check_ad_options_cb = CallbackData('ad_options', 'ad_id', 'vendor', 'tip_id')
action_on_ad_cb = CallbackData('setup_ad', 'action', 'ad_id')


# ----- Handlers for creating normal ParentingTip ------
async def add_new_article(call: types.CallbackQuery, state: FSMContext):

    await state.finish()

    await call.message.answer("Добавляем новую статью.\n\n Для начала введите заголовок", reply_markup=cancel_kb)
    await state.set_state(Article.header.state)


async def set_header(message: types.Message, state: FSMContext):
    header = message.text
    await state.update_data(header=header)
    await state.set_state(Article.tip.state)
    await message.answer("Заголовок есть. Теперь заготовленный текст статьи", reply_markup=cancel_kb)


async def set_body(message: types.Message, state: FSMContext):
    body = message.text
    await state.update_data(tip=body)
    await state.set_state(Article.category.state)

    reply_kb = show_categories(no_cancel=True)
    from config import PRENATAL_CATEGORIES
    new_buttons = [InlineKeyboardButton(text=item[0], callback_data=item[1]) for item in PRENATAL_CATEGORIES]

    reply_kb.add(*new_buttons)
    reply_kb.add(InlineKeyboardButton("Отмена", callback_data="cancel"))

    await message.answer("Текст есть. Выберите категорию", reply_markup=reply_kb)


async def set_category(call: types.CallbackQuery, state: FSMContext):
    category = call.data

    await state.update_data(category=category)
    await state.set_state(Article.age_range.state)

    reply_kb = ages_keyboard()
    reply_kb.add(InlineKeyboardButton("Отмена", callback_data="cancel"))

    await call.message.edit_text("Категория есть. Выберите возраст",
                         reply_markup=reply_kb)


async def set_age_inline(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    from_day = callback_data['from_day']
    until_day = callback_data['until_day']

    article_data = await state.get_data()

    success = create_new_article(article_data, from_day, until_day)
    logger.info(f"Added new article: {success.header} in category {success.category} for age from {success.useful_from_day} to {success.useful_until_day} by admin {call.from_user.id}")
    if not success:
        await call.message.edit_text("Something went wrong. Article was not saved")
        logger.error(f"New article: {success.header} created by admin {call.from_user.id} wasn't saved for some reason. Function create_new_article returned False")
        return

    await state.finish()
    await call.message.edit_text("Новая статья сохранена", reply_markup=admin_kb)


# ------ Handlers for creating DailyTip --------

async def list_daily_tips(call: types.CallbackQuery):
    daily_tip_summary_list = get_list_of_daily_tips()
    if len(daily_tip_summary_list) == 0:
        await call.message.answer("Нет статей")
        return
    answer_text = ""

    for tip in daily_tip_summary_list:
        answer_text += f"{tip}"
    await call.message.answer(answer_text)


async def render_daily_tip(message: types.Message):
    daily_tip_id = message.text.split()[-1]
    try:
        int(daily_tip_id)
    except ValueError:
        await message.answer("Введённый id не является числом")
        return

    daily_tip = get_daily_tip_by_id(int(daily_tip_id))

    if not daily_tip:
        await message.answer("Такой статьи с таким ID")
        return

    final_message = handle_daily_article(daily_tip)

    if final_message['media']:

        text = f"<b>{final_message['header']}</b>\n\n{final_message['body']}"
        await message.bot.send_photo(message.from_user.id, final_message['media'], caption=text, parse_mode="HTML")

    else:
        final_message = f"<b>{daily_tip.header}</b>\n\n{daily_tip.body}"
        await message.bot.send_message(chat_id=message.from_user.id, text=final_message, parse_mode='HTML')


async def delete_daily_tip(message: types.Message):
    daily_tip_id = message.text.split()[-1]
    try:
        int(daily_tip_id)
    except ValueError:
        await message.answer("Введённый id не является числом")
        return

    logger.info(f"Prepared to delete daily tip with ID {daily_tip_id}")
    success = delete_daily_tip_by_id(int(daily_tip_id))
    if success:
        logger.info(f"Daily tip with ID {daily_tip_id} was successfully deleted by admin {message.from_user.id}")
        await message.answer("Статья успешно удалена")
    else:
        await message.answer("При удалении возникла ошибка. Чекайте логи.")



async def add_new_daily_article(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Добавляем новую статью, которая будет приходить когда зарегистрированному ребёнку исполнится столько-то дней. Введите заголовок",
                         reply_markup=cancel_kb)
    await state.set_state(DailyArticle.header.state)


async def header_input(message: types.Message, state: FSMContext):
    await state.update_data(header=message.text)
    await state.set_state(DailyArticle.body.state)
    await message.answer(f"Получил заголовок: {message.text}. Он будет выделен жирным. Теперь введите тело статьи",
                         reply_markup=cancel_kb)


async def body_input(message: types.Message, state: FSMContext):
    await state.update_data(body=message.text)
    await state.set_state(DailyArticle.age_in_days.state)
    await message.answer(f"Получил основную статью. Теперь введите цифру, в какой день нужно её отослать пользователю. "
                         f"Это должен быть возраст ребёнка в днях, например, 56",
                         reply_markup=cancel_kb)


async def age_in_days_input(message: types.Message, state: FSMContext):
    age_in_days = message.text

    # validate input, should be integer
    correct_age = validate_age(age_in_days)

    await state.update_data(age_in_days=correct_age)
    await state.set_state(DailyArticle.media.state)
    await message.answer(f"Получил возраст: {correct_age}. Если статья была небольшая, то можно добавить картинку или видео."
                         f"Залейте картинку без подписи или введите команду /media_pass",
                         reply_markup=cancel_kb)


async def add_media_for_daily_tip(message: types.Message, state: FSMContext):

    file_id = message.photo[-1].file_id

    state_data: dict = await state.get_data()
    state_data['file_id'] = file_id

    create_daily_tip(**state_data)

    state_data = await state.get_data()

    await message.answer_photo(file_id,
                               caption=f"Успешно добавил новую статью.\n"
                                       f"Название: {state_data['header']}. \nПошлю когда ребёнку будет {state_data['age_in_days']} дней.\n"
                                       f"Прикрепляю добавленное изображение")
    await state.finish()


async def pass_media(message: types.Message, state: FSMContext):
    state_data: dict = await state.get_data()
    state_data['file_id'] = ""
    await message.answer(f"Успешно добавил новую статью.\n"
                         f"Название: {state_data['header']}. \nПошлю когда ребёнку будет {state_data['age_in_days']} дней.\n"
                         f"В статье не будет картинки")
    create_daily_tip(**state_data)
    await state.finish()


# Handlers to retrieve statistics
async def get_statistics_by_article(call: types.CallbackQuery, callback_data: dict):
    article_id = int(callback_data['tip_id'])
    analytic_data: dict = db_analytics.get_article_statistics(article_id)

    text = f"""
    Уникальных просмотров статьи:
    {analytic_data['today']} за сегодня;
    {analytic_data['yesterday']} за вчера;
    {analytic_data['last_week']} за 7 дней;
    {analytic_data['last_month']} за 30 дней;
    {analytic_data['total']} за всё время;
    """

    await call.message.edit_text(text, reply_markup=article_actions_keyboard(article_id))


async def get_active_users_statistics(call: types.CallbackQuery):
    time_range_today = get_hours_passed_today()
    active_users_today = get_active_users('hours', time_range_today)
    active_users_seven_days = get_active_users('days', 7)

    text = f"""
    За сегодня {active_users_today} пользователей выбирали категорию;
    За 7 дней {active_users_seven_days} пользователей выбирали категорию.
    """



    await call.message.answer(text)

async def get_most_viewed_parenting_tips(call: types.CallbackQuery):
    most_viewed_tips = get_most_viewed_tips()
    text = ""
    for tip in most_viewed_tips:
        text += f"{tip['header']}. {tip['view_count']} просмотров.\n"

    await call.message.answer(text)

async def get_registration_statistics(call: types.CallbackQuery):
    statistics: dict = get_user_registration_stats()


    text = f"""
    За сегодня зарегистрировано {statistics['today_count']} пользователей;
    За прошлый день зарегистрировано {statistics['yesterday_count']} пользователей;
    За 7 дней зарегистрировано {statistics['seven_days_count']} пользователей;
    За 30 дней зарегистрировано {statistics['thirty_days_count']} пользователей;
    За всё время зарегистрировано {statistics['total_count']} пользователей.
    """

    await call.message.answer(text)


# Handlers to create new short Advice (ChildAdvice)

async def cmd_new_advice(call: types.CallbackQuery):
    await call.message.answer("Добавляем новый короткий совет. Они показываются детям в определённый период. Например, с "
                         "1 дня жизни до 30 дня жизни. Введите нижную планку границы - одно число от 0 до 180",
                         reply_markup=cancel_kb)
    await Advice.age_range_start.set()


async def set_are_range_start(message: types.Message, state: FSMContext):
    try:
        age_range_start = int(message.text)
        await state.update_data(age_range_start=age_range_start)
        await message.answer("Есть. Теперь введите конец возрастного диапазона (целое число):",
                             reply_markup=cancel_kb)
        await Advice.age_range_end.set()
    except ValueError:
        await message.answer("Пожалуйста, введите целое число.",
                             reply_markup=cancel_kb)


async def set_age_range_end(message: types.Message, state: FSMContext):
    try:
        age_range_end = int(message.text)
        await state.update_data(age_range_end=age_range_end)
        await message.answer("Есть. Теперь введите сам текст",
                             reply_markup=cancel_kb)
        await Advice.advice.set()
    except ValueError:
        await message.answer("Пожалуйста, введите целое число.",
                             reply_markup=cancel_kb)


async def set_advice(message: types.Message, state: FSMContext):
    advice = message.text
    await state.update_data(advice=advice)

    # Get the data collected so far.
    data = await state.get_data()
    add_new_advice(
        age_start=data['age_range_start'],
        age_end=data['age_range_end'],
        advice_text=data['advice']
    )

    await message.answer(f"Совет:\n{data['advice']}\n..добавлен. Он будет показан когда возраст ребёнка будет между "
                         f"{data['age_range_start']} и {data['age_range_end']} дней")

    await state.finish()


# Handlers for deleting a tip
async def delete_tip(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.finish()
    tip_id = callback_data['tip_id']

    await state.update_data(tip_id=tip_id)


    mark = InlineKeyboardMarkup()
    confirm = InlineKeyboardButton(
        text="Подтвердить",
        callback_data="confirm_deleting_tip"
    )
    cancel = InlineKeyboardButton(
        text="Отмена",
        callback_data="cancel_deleting_tip"
    )
    mark.add(confirm, cancel)

    await state.set_state(DeleteArticle.confirm.state)
    await call.message.edit_text("Вы уверены, что хотите удалить совет?", reply_markup=mark)


async def confirm_deleting_tip(call: types.CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    tip_id = state_data['tip_id']

    tips_crud.delete_tip(tip_id)
    await call.message.edit_text("Совет был удалён", reply_markup=main_keyboard_registered(call.from_user.id))
    await state.finish()


async def cancel_deleting_tip(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Удаление отменено", reply_markup=main_keyboard_registered(call.from_user.id))
    await state.finish()


# Handlers for editing tip text
async def start_tip_content_editing(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.finish()

    tip_id = callback_data['tip_id']
    tip = tips_crud.get_tip_by_id(tip_id)

    formatter = TipRenderer(tip)
    message_text: str = formatter.form_final_text()

    await call.message.edit_text(message_text)
    await call.message.answer("Выше то, как статья выглядит сейчас. \nПришлите отредактированный текст новым сообщением")

    await state.update_data(tip=tip)
    await state.set_state(EditArticle.new_text.state)



async def update_tip(message: types.Message, state: FSMContext):
    edited_text = message.text
    await state.update_data(new_text=edited_text)

    mark = InlineKeyboardMarkup()
    confirm = InlineKeyboardButton(
        text="Подтвердить",
        callback_data="confirm_edited_tip"
    )
    cancel = InlineKeyboardButton(
        text="Отмена",
        callback_data="cancel_edited_tip"
    )
    mark.add(confirm, cancel)

    await message.answer("Получил обновлённый текст. Посмотрите на сообщение выше и подтвердите либо отмените редактирование",
                         reply_markup=mark)
    await state.set_state(EditArticle.confirm.state)


async def confirm_edited_tip(call: types.CallbackQuery, state: FSMContext):
    print("edit tip confirmation ran")
    tip_info = await state.get_data()
    tip_id: ParentingTip = tip_info['tip'].id

    tips_crud.update_tip_text(tip_id, tip_info['new_text'])
    await call.message.edit_text("Текст статьи обновлён", reply_markup=main_keyboard_registered(call.from_user.id))
    await state.finish()

async def cancel_edited_tip(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Обновление статьи отменено", reply_markup=main_keyboard_registered(call.from_user.id))


# Handlers for adding advertisements
async def add_new_ad_for_article(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await state.finish()
    tip_id = callback_data['tip_id']

    Advertisement.tip_id=tip_id
    # await Advertisement.tip_id.set()
    # await state.update_data(tip_id=tip_id)
    await Advertisement.ad_text.set()
    await state.update_data(tip_id=tip_id)

    logger.info(f"Stared adding new ad process for tip ID: {tip_id}")
    await call.message.edit_text(f"Добавляем новую рекламу к статье с ID: {tip_id}. Введите текст рекламы.")


async def add_text_to_ad(message: types.Message, state: FSMContext):
    ad_text = message.text
    logger.info(f"Got ad text: {ad_text}")
    await state.update_data(ad_text=ad_text)

    await message.answer(f"Есть! Укажите сколько дней будет действовать реклама. Введите одно число")
    await Advertisement.active_period.set()


async def set_ad_show_period(message: types.Message, state: FSMContext):
    try:
        ad_active_for = int(message.text)
        await state.update_data(active_period=ad_active_for)
        await message.answer("Ок. Теперь введите имя заказчика - его можно будет найти в панели администрирование реклам.")
        await Advertisement.vendor.set()

    except ValueError:
        await message.answer(f"Пожалуйста, введите длительноть в днях. Одно число.")


async def set_ad_vendor(message: types.Message, state: FSMContext):
    vendor_name = message.text

    await state.update_data(vendor=vendor_name)

    mark = InlineKeyboardMarkup()
    confirm = InlineKeyboardButton(
        text="Подтвердить",
        callback_data="confirm_new_ad"
    )
    cancel = InlineKeyboardButton(
        text="Отмена",
        callback_data="cancel_new_ad"
    )

    mark.add(confirm, cancel)

    ad_data = await state.get_data()

    await message.answer(f"Добавляем новую рекламу:\n\n{ad_data['ad_text']}\n\n ...к статье: {Advertisement.tip_id} на "
                         f"период в {ad_data['active_period']} дней. Заказчик: {ad_data['vendor']}. Вы уверены?",
                         reply_markup=mark)

    await Advertisement.confirm.set()

async def confirm_new_ad(call: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    print(data)

    # tips_crud.update_advertisement(data['tip_id'], data['text'])
    ads_crud.add_advertisement_to_tip(

        data['tip_id'],
        data['ad_text'],
        data['vendor'],
        data['active_period']
    )

    await state.finish()
    await call.message.edit_text("Реклама успешно добавлена",
                                 reply_markup=admin_kb)


async def cancel_new_ad(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Добавление рекламы отменено",
                                 reply_markup=admin_kb)


# Handlers for ads panel
async def advertisement_control_panel(call: types.CallbackQuery):

    ads = ads_crud.get_all_ads()

    mark = InlineKeyboardMarkup(row_width=1)
    ad_buttons = [InlineKeyboardButton(text=ad.vendor_name,
                                       callback_data=check_ad_options_cb.new(ad_id=ad.id,
                                                                             vendor=ad.vendor_name,
                                                                             tip_id=ad.tip_id)
                                       ) for ad in ads]

    cancel = InlineKeyboardButton(text="Назад", callback_data='cancel')

    mark.add(*ad_buttons)
    mark.add(cancel)

    await call.message.edit_text(f"Список всех активных реклам на данный момент.",
                                 reply_markup=mark)


async def setup_advertisement(call: types.CallbackQuery, callback_data: dict):
    text = f"""
ID рекламы: {callback_data['ad_id']} 
Реклама от заказчика: {callback_data['vendor']}
Реклама в статье: {callback_data['tip_id']}

Выберите действие.
    """

    mark = InlineKeyboardMarkup(row_width=2)

    delete_ad = InlineKeyboardButton(text="Удалить рекламу",
                                     callback_data=action_on_ad_cb.new(action='delete', ad_id=callback_data['ad_id']))

    see_ad_statistics = InlineKeyboardButton(text="Посмотреть статистику",
                                             callback_data=action_on_ad_cb.new(action='statistics', ad_id=callback_data['ad_id']))

    prolongate_ad = InlineKeyboardButton(text="Продлить срок действия",
                                         callback_data=action_on_ad_cb.new(action='prolongate', ad_id=callback_data['ad_id']))

    back = InlineKeyboardButton(text="Назад",
                                callback_data='cancel')

    mark.add(delete_ad, prolongate_ad).add(see_ad_statistics, back)

    await call.message.edit_text(text, reply_markup=mark)


async def see_ad_statistics(call: types.CallbackQuery, callback_data: dict):
    logger.info(f"{callback_data}")
    stat: dict = ads_crud.count_ad_shows(callback_data['ad_id'])

    text = f"""
Просмотров рекламы за сегодня: {stat['today']}
Просмотров рекламы за вчера: {stat['yesterday']}
Просмотров рекламы за 7 дней: {stat['last_week']}
Просмотров рекламы за 30 дней: {stat['last_month']}
Просмотров рекламы за всё время: {stat['all_time']}

    """
    await call.message.edit_text(text, reply_markup=cancel_kb)


async def delete_advertisement(call: types.CallbackQuery, callback_data: dict):
    """
    handler deletes given advertisement from db
    :param call:
    :param callback_data:
    :return:
    """
    deleted = ads_crud.delete_advertisement(callback_data['ad_id'])
    if deleted:
        await call.message.edit_text(f"Реклама с айди {callback_data['ad_id']} была удалена.",
                                     reply_markup=admin_kb)
        logger.info(f"Admin ID {call.from_user.id} deleted advertisement with ID {callback_data['ad_id']}")
    else:
        await call.message.edit_text(f"Произошла ошибка при удалении. Реклама не удалена.",
                                     reply_markup=admin_kb)
        logger.error(f"Admin ID {call.from_user.id} tried to delete ad ID {callback_data['ad_id']}. Error occured.")


# Handlers for sending one-time message to all users
async def send_one_time_message(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Вы собираетесь отправить сообщение всем пользователям. Если планируется картинка, отправьте "
                              "сначала её без описания", reply_markup=cancel_kb)
    await state.set_state(OneTimeMessage.media.state)

    logger.warning(f"Admin ID {call.from_user.id} starts process of sending message to all users")

async def set_one_time_ad_media(message: types.Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await message.answer("Получил картинку. Текст описания к ней не может превышать  1 024 символа. Отправьте текст.",
                         reply_markup=cancel_kb)

    await state.update_data(media=file_id)
    await state.set_state(OneTimeMessage.body.state)


async def set_one_time_ad_body(message: types.Message, state: FSMContext):
    ad_body = message.text
    await state.update_data(body=ad_body)
    await state.set_state(OneTimeMessage.body.state)
    await message.answer('Получил данные статьи. Посмотрите, всё ли верно и, если да, нажмите "Подтвердить"')


    confirm_sending = InlineKeyboardButton(text="Подтвердить", callback_data="confirm_ad_sending")
    cancel_sending = InlineKeyboardButton(text="Отмена", callback_data="cancel_ad_sending")
    mark = InlineKeyboardMarkup().add(confirm_sending, cancel_sending)

    ad_data = await state.get_data()
    mediafile = ad_data['media']

    if not mediafile:
        await message.answer(ad_body, reply_markup=mark)
        await state.set_state(OneTimeMessage.confirm.state)
        return

    await message.answer_photo(mediafile, caption=ad_body, reply_markup=mark)
    await state.set_state(OneTimeMessage.confirm.state)

    logger.info("Prepared a text for sending to all users. Waiting for confirmation")


async def confirm_one_time_msg_sending(call: types.CallbackQuery, state: FSMContext):
    users_list = user_crud.get_all_users()
    article_data = await state.get_data()
    has_media = article_data.get('media')
    if not has_media:
        for user in users_list:
            await call.bot.send_message(user.telegram_user_id, article_data['body'])
    else:
        for user in users_list:
            try:
                await call.bot.send_photo(user[0], article_data['media'], caption=article_data['body'])
                await asyncio.sleep(0.1)
            except aiogram.utils.exceptions.ChatNotFound:
                continue

    logger.warning(f"Sent a message with content: \n{article_data['body']} \nto all users")
    await call.bot.send_message(ADMINS[0], "Message sent successfully to all users")
    await state.finish()


async def cancel_one_time_msg_sending(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Отправка сообщения всем пользователям отменена")
    # Sending message payload to separate function which uses bot obj to send
    await state.finish()


# Handlers for admin menu navigation
async def open_admin_panel(call: types.CallbackQuery):
    await call.message.edit_text("Добро пожаловать в админ панель", reply_markup=admin_kb)


async def cancel_any_input(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Действие отменено", reply_markup=admin_kb)


def register_admin_hanlders(dp: Dispatcher):
    # Handlers for admin menu navigation
    dp.register_callback_query_handler(cancel_any_input, Text(equals="cancel"), state='*', user_id=ADMINS)
    dp.register_callback_query_handler(open_admin_panel, Text(equals="admin_menu"), user_id=ADMINS)

    # Handlers for sending one-time message to all users:
    dp.register_callback_query_handler(send_one_time_message, Text(equals="send_one_time_media"), state="*", user_id=ADMINS)
    dp.register_message_handler(set_one_time_ad_media, content_types=['photo'], state=OneTimeMessage.media)
    dp.register_message_handler(set_one_time_ad_body, state=OneTimeMessage.body)
    dp.register_callback_query_handler(confirm_one_time_msg_sending, Text(equals="confirm_ad_sending"), state=OneTimeMessage.confirm)
    dp.register_callback_query_handler(cancel_one_time_msg_sending, Text(equals="cancel_ad_sending"), state=OneTimeMessage.confirm)

    # Handlers for editing Tip text:
    dp.register_callback_query_handler(start_tip_content_editing, edit_tip_cb.filter(), state="*", user_id=ADMINS)
    dp.register_message_handler(update_tip, state=EditArticle.new_text)
    dp.register_callback_query_handler(confirm_edited_tip, Text(equals="confirm_edited_tip"), state=EditArticle.confirm)
    dp.register_callback_query_handler(cancel_edited_tip, Text(equals="cancel_edited_tip"), state=EditArticle.confirm)

    # Handlers for deleting Tip:
    dp.register_callback_query_handler(delete_tip, delete_tip_cb.filter(), state="*", user_id=ADMINS)
    dp.register_callback_query_handler(confirm_deleting_tip, Text(equals="confirm_deleting_tip"), state=DeleteArticle.confirm)
    dp.register_callback_query_handler(cancel_deleting_tip, Text(equals="cancel_deleting_tip"), state=DeleteArticle.confirm)

    # Handlers for adding new advertisement to ParentingTip:
    dp.register_callback_query_handler(add_new_ad_for_article, add_advertisement_cb.filter(), state="*", user_id=ADMINS)
    dp.register_message_handler(add_text_to_ad, state=Advertisement.ad_text)
    dp.register_message_handler(set_ad_show_period, state=Advertisement.active_period)
    dp.register_message_handler(set_ad_vendor, state=Advertisement.vendor)
    dp.register_callback_query_handler(confirm_new_ad, Text(equals="confirm_new_ad"), state=Advertisement.confirm)
    dp.register_callback_query_handler(cancel_new_ad, Text(equals="cancel_new_ad"), state=Advertisement.confirm)


    # Handlers for ads panel
    dp.register_callback_query_handler(advertisement_control_panel, Text(equals="ad_control_panel"), user_id=ADMINS)
    dp.register_callback_query_handler(setup_advertisement, check_ad_options_cb.filter())
    dp.register_callback_query_handler(delete_advertisement, action_on_ad_cb.filter(action='delete'))

    # Handlers for creating normal ParentingTip
    dp.register_callback_query_handler(add_new_article, Text(equals="add_material"), user_id=ADMINS)
    dp.register_message_handler(set_header, state=Article.header.state)
    dp.register_message_handler(set_body, state=Article.tip.state)
    dp.register_callback_query_handler(set_category, state=Article.category.state)
    dp.register_callback_query_handler(set_age_inline, get_ages_cb.filter(), state=Article.age_range.state)

    # Handlers for handling DailyTip
    dp.register_callback_query_handler(add_new_daily_article, Text(equals="add_daily"), user_id=ADMINS)
    dp.register_message_handler(add_new_daily_article, commands=['new_daily'], state='*')
    dp.register_message_handler(header_input, state=DailyArticle.header)
    dp.register_message_handler(body_input, state=DailyArticle.body)
    dp.register_message_handler(age_in_days_input, state=DailyArticle.age_in_days)
    dp.register_message_handler(pass_media, commands=['media_pass'], state=DailyArticle.media)
    dp.register_message_handler(add_media_for_daily_tip, content_types=['photo'], state=DailyArticle.media)
    # handlers others from creation handling
    dp.register_callback_query_handler(list_daily_tips, Text(equals="list_daily"), user_id=ADMINS)
    dp.register_message_handler(delete_daily_tip, Text(startswith="delete_daily_tip"), user_id=ADMINS)
    dp.register_message_handler(render_daily_tip, Text(startswith="render_daily"))


    # Handlers for creating short advices (ChildAdvice model)
    dp.register_callback_query_handler(cmd_new_advice, Text(equals="add_advice"), user_id=ADMINS)
    dp.register_message_handler(cmd_new_advice, commands=['new_advice'])
    dp.register_message_handler(set_are_range_start, state=Advice.age_range_start)
    dp.register_message_handler(set_age_range_end, state=Advice.age_range_end)
    dp.register_message_handler(set_advice, state=Advice.advice)

    # Handlers to retrieve analytics
    dp.register_callback_query_handler(get_statistics_by_article, admin_statistics_cb.filter(), state='*')
    dp.register_callback_query_handler(get_active_users_statistics, Text(equals="active_users_statistics"), user_id=ADMINS)
    dp.register_callback_query_handler(get_registration_statistics, Text(equals="registered_users_statistics"), user_id=ADMINS)
    dp.register_callback_query_handler(see_ad_statistics, action_on_ad_cb.filter(action='statistics'), user_id=ADMINS)
    dp.register_callback_query_handler(get_most_viewed_parenting_tips, Text(equals='top_10_articles'), user_id=ADMINS)