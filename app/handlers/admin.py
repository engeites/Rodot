from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton

from app.database.advice_crud import add_new_advice
from app.database.user_crud import get_active_users
from app.extentions import logger, ADMINS
from app.keyboards.inline.admin_kb import admin_kb, cancel_kb
from app.keyboards.inline.main_kb_inline import categories_kb
from app.utils.time_ranges import get_hours_passed_today
from app.utils.validators import validate_age, validate_category
from app.database.tips_crud import create_new_article
from app.database.daily_tips_crud import create_daily_tip
from app.database import db_analytics

from app.keyboards.inline.ages import ages_keyboard, get_ages_cb
from app.keyboards.inline.bookmarks import admin_statistics_cb, add_bookmark_keyboard


# StatesGroup for normal articles
class Article(StatesGroup):
    """
    Represents StatesGroup for normal ParentinTip
    """
    header = State()
    tip = State()
    category = State()
    age_range = State()


# StatesGroup for Daily article
class DailyArticle(StatesGroup):
    """
    Represents StatesGroup for daily articles
    """
    header = State()
    body = State()
    age_in_days = State()
    media = State()


# StatesGroup for Short Advice
class Advice(StatesGroup):
    age_range_start = State()
    age_range_end = State()
    advice = State()



# ----- Handlers for creating normal ParentingTip ------
async def add_new_article(call: types.CallbackQuery, state: FSMContext):

    await state.finish()
    # This should filter users and respond to admin only

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

    reply_kb = categories_kb.copy()
    reply_kb.add(InlineKeyboardButton("Отмена", callback_data="cancel"))

    await message.answer("Текст есть. Выберите категорию", reply_markup=reply_kb)


async def set_category(call: types.CallbackQuery, state: FSMContext):
    category = call.data


    await state.update_data(category=validate_category(category))
    await state.set_state(Article.age_range.state)

    reply_kb = ages_keyboard.copy()
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

    await call.message.edit_text(text, reply_markup=add_bookmark_keyboard(article_id))


async def get_active_users_statistics(call: types.CallbackQuery):
    time_range_today = get_hours_passed_today()
    active_users_today = get_active_users('hours', time_range_today)
    active_users_seven_days = get_active_users('days', 7)

    text = f"""
    За сегодня {active_users_today} пользователей выбирали категорию;
    За 7 дней {active_users_seven_days} пользователей выбирали категорию.
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


# Handlers for admin menu navigation
async def open_admin_panel(call: types.CallbackQuery):
    await call.message.edit_text("Добро пожаловать в админ панель", reply_markup=admin_kb)



async def cancel_any_input(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Действие отменено", reply_markup=admin_kb)


def register_admin_hanlders(dp: Dispatcher):
    # Handlers for admin menu navigation
    dp.register_callback_query_handler(cancel_any_input, Text(equals="cancel"), state='*')
    dp.register_callback_query_handler(open_admin_panel, Text(equals="admin_menu"))


    # Handlers for creating normal ParentingTip
    dp.register_callback_query_handler(add_new_article, Text(equals="add_material"))
    dp.register_message_handler(set_header, state=Article.header.state)
    dp.register_message_handler(set_body, state=Article.tip.state)
    dp.register_callback_query_handler(set_category, state=Article.category.state)
    dp.register_callback_query_handler(set_age_inline, get_ages_cb.filter(), state=Article.age_range.state)

    # Handlers for creating DailyTip
    dp.register_callback_query_handler(add_new_daily_article, Text(equals="add_daily"))
    dp.register_message_handler(add_new_daily_article, commands=['new_daily'], state='*')
    dp.register_message_handler(header_input, state=DailyArticle.header)
    dp.register_message_handler(body_input, state=DailyArticle.body)
    dp.register_message_handler(age_in_days_input, state=DailyArticle.age_in_days)
    dp.register_message_handler(pass_media, commands=['media_pass'], state=DailyArticle.media)
    dp.register_message_handler(add_media_for_daily_tip, content_types=['photo'], state=DailyArticle.media)

    # Handlers for creating short advices (ChildAdvice model)
    dp.register_callback_query_handler(cmd_new_advice, Text(equals="add_advice"))
    dp.register_message_handler(cmd_new_advice, commands=['new_advice'])
    dp.register_message_handler(set_are_range_start, state=Advice.age_range_start)
    dp.register_message_handler(set_age_range_end, state=Advice.age_range_end)
    dp.register_message_handler(set_advice, state=Advice.advice)

    # Handlers to retrieve analytics
    dp.register_callback_query_handler(get_statistics_by_article, admin_statistics_cb.filter(), state='*')
    dp.register_callback_query_handler(get_active_users_statistics, Text(equals="active_users_statistics"), user_id=ADMINS)
