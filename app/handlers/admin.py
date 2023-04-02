import os
import io

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import PhotoSize

from app.config import ADMINS
from app.database.advice_crud import add_new_advice
from app.database.user_crud import get_active_users
from app.keyboards.inline.main_kb_inline import categories_kb
from app.utils.time_ranges import get_hours_passed_today
from app.utils.validators import validate_age, validate_category
from app.database.tips_crud import create_new_article
from app.database.daily_tips_crud import create_daily_tip
from app.database import db_analytics

from app.keyboards.inline.ages import ages_keyboard, cb
from app.keyboards.inline.bookmarks import admin_statistics_cb, add_bookmark_keyboard


# StatesGroup for normal articles
class Article(StatesGroup):
    """
    Represents StatesGroup for normal ParentinTip
    """
    header = State()
    tip = State()
    tags = State()
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


class Advice(StatesGroup):
    age_range_start = State()
    age_range_end = State()
    advice = State()

# ----- Handlers for creating normal ParentingTip ------
async def add_new_article(message: types.Message, state: FSMContext):

    await state.finish()
    # This should filter users and respond to admin only

    await message.answer("Добавляем новую статью.\n\n Для начала введите заголовок")
    await state.set_state(Article.header.state)


async def set_header(message: types.Message, state: FSMContext):
    header = message.text
    await state.update_data(header=header)
    await state.set_state(Article.tip.state)
    await message.answer("Заголовок есть. Теперь заготовленный текст статьи")


async def set_body(message: types.Message, state: FSMContext):
    body = message.text
    await state.update_data(tip=body)
    await state.set_state(Article.tags.state)
    await message.answer("Текст есть. Выберите категорию", reply_markup=categories_kb)


async def set_tags(call: types.CallbackQuery, state: FSMContext):
    tags = call.data


    await state.update_data(tags=validate_category(tags))
    await state.set_state(Article.age_range.state)
    await call.message.edit_text("Категория есть. Выберите возраст",
                         reply_markup=ages_keyboard)


async def set_age_inline(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    from_day = callback_data['from_day']
    until_day = callback_data['until_day']

    article_data = await state.get_data()

    success = create_new_article(article_data, from_day, until_day)
    print([tag.name for tag in success.tags])
    if not success:
        await call.message.edit_text("Something went wrong. Article was not saved")
        return

    await state.finish()
    await call.message.edit_text("Новая статья сохранена")


# ------ Handlers for creating DailyTip --------

async def add_new_daily_article(message: types.Message, state: FSMContext):
    await message.answer("Добавляем новую статью, которая будет приходить когда зарегистрированному ребёнку исполнится столько-то дней. Введите заголовок")
    await state.set_state(DailyArticle.header.state)


async def header_input(message: types.Message, state: FSMContext):
    await state.update_data(header=message.text)
    await state.set_state(DailyArticle.body.state)
    await message.answer(f"Получил заголовок: {message.text}. Он будет выделен жирным. Теперь введите тело статьи")


async def body_input(message: types.Message, state: FSMContext):
    await state.update_data(body=message.text)
    await state.set_state(DailyArticle.age_in_days.state)
    await message.answer(f"Получил основную статью. Теперь введите цифру, в какой день нужно её отослать пользователю. "
                         f"Это должен быть возраст ребёнка в днях, например, 56")


async def age_in_days_input(message: types.Message, state: FSMContext):
    age_in_days = message.text

    # validate input, should be integer
    correct_age = validate_age(age_in_days)

    await state.update_data(age_in_days=correct_age)
    await state.set_state(DailyArticle.media.state)
    await message.answer(f"Получил возраст: {correct_age}. Если статья была небольшая, то можно добавить картинку или видео."
                         f"Залейте картинку без подписи или введите команду /media_pass")




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
    Статья была прочитана:
    {analytic_data['today']} раз за сегодня;
    {analytic_data['yesterday']} раз за вчера;
    {analytic_data['last_week']} раз за 7 дней;
    {analytic_data['last_month']} раз за 30 дней;
    {analytic_data['total']} раз за всё время;
    """

    await call.message.edit_text(text, reply_markup=add_bookmark_keyboard(article_id))


async def get_active_users_statistics(message: types.Message):
    time_range_today = get_hours_passed_today()
    active_users_today = get_active_users('hours', time_range_today)
    active_users_seven_days = get_active_users('days', 7)

    text = f"""
    За сегодня {active_users_today} пользователей выбирали категорию;
    За 7 дней {active_users_seven_days} пользователей выбирали категорию.
    """

    await message.answer(text)


# Handlers to create new short Advice (ChildAdvice)

async def cmd_new_advice(message: types.Message):
    await message.answer("Добавляем новый короткий совет. Они показываются детям в определённый период. Например, с "
                         "1 дня жизни до 30 дня жизни. Введите нижную планку границы - одно число от 0 до 180")
    await Advice.age_range_start.set()


async def set_are_range_start(message: types.Message, state: FSMContext):
    try:
        age_range_start = int(message.text)
        await state.update_data(age_range_start=age_range_start)
        await message.answer("Есть. Теперь введите конец возрастного диапазона (целое число):")
        await Advice.age_range_end.set()
    except ValueError:
        await message.answer("Пожалуйста, введите целое число.")


async def set_age_range_end(message: types.Message, state: FSMContext):
    try:
        age_range_end = int(message.text)
        await state.update_data(age_range_end=age_range_end)
        await message.answer("Есть. Теперь введите сам текст")
        await Advice.advice.set()
    except ValueError:
        await message.answer("Пожалуйста, введите целое число.")


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



def register_admin_hanlders(dp: Dispatcher):
    # Handlers for creating normal ParentingTip
    dp.register_message_handler(add_new_article, commands=['new'], state='*')
    dp.register_message_handler(set_header, state=Article.header.state)
    dp.register_message_handler(set_body, state=Article.tip.state)
    dp.register_callback_query_handler(set_tags, state=Article.tags.state)
    dp.register_callback_query_handler(set_age_inline, cb.filter(), state=Article.age_range.state)

    # Handlers for creating DailyTip
    dp.register_message_handler(add_new_daily_article, commands=['new_daily'], state='*')
    dp.register_message_handler(header_input, state=DailyArticle.header)
    dp.register_message_handler(body_input, state=DailyArticle.body)
    dp.register_message_handler(age_in_days_input, state=DailyArticle.age_in_days)
    dp.register_message_handler(pass_media, commands=['media_pass'], state=DailyArticle.media)
    dp.register_message_handler(add_media_for_daily_tip, content_types=['photo'], state=DailyArticle.media)

    # Handlers for creating short advices (ChildAdvice model)
    dp.register_message_handler(cmd_new_advice, commands=['new_advice'])
    dp.register_message_handler(set_are_range_start, state=Advice.age_range_start)
    dp.register_message_handler(set_age_range_end, state=Advice.age_range_end)
    dp.register_message_handler(set_advice, state=Advice.advice)

    # Handlers to retrieve analytics
    dp.register_callback_query_handler(get_statistics_by_article, admin_statistics_cb.filter(), state='*')
    dp.register_message_handler(get_active_users_statistics, commands=['active_users'], user_id=ADMINS)