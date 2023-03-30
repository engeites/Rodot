import os
import io

from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import PhotoSize

from app.utils.validators import validate_age
from app.database.tips_crud import create_new_article
from app.database.daily_tips_crud import create_daily_tip

from app.keyboards.inline.ages import ages_keyboard, cb

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


# ----- Handlers for creating normal ParentingTip ------
async def add_new_article(message: types.Message, state: FSMContext):

    await state.finish()
    # This should filter users and respond to admin only

    await message.answer("Adding new article to knowledge base.\n\n First, input a header")
    await state.set_state(Article.header.state)


async def set_header(message: types.Message, state: FSMContext):
    header = message.text
    await state.update_data(header=header)
    await state.set_state(Article.tip.state)
    await message.answer("Got the header. Please send full article text")


async def set_body(message: types.Message, state: FSMContext):
    body = message.text
    await state.update_data(tip=body)
    await state.set_state(Article.tags.state)
    await message.answer("Got the article text. Please send tags. Divide by comma (,)")


async def set_tags(message: types.Message, state: FSMContext):
    tags = message.text
    await state.update_data(tags=tags)
    await state.set_state(Article.age_range.state)
    await message.answer("Got the tags list. Now please send the age when this article is useful",
                         reply_markup=ages_keyboard)


async def set_age_inline(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    from_day = callback_data['from_day']
    until_day = callback_data['until_day']

    article_data = await state.get_data()

    success = create_new_article(article_data, from_day, until_day)

    if not success:
        await call.message.edit_text("Something went wrong. Article was not saved")
        return

    await state.finish()
    await call.message.edit_text("New article is successfully saved")


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


def register_admin_hanlders(dp: Dispatcher):
    # States for creating normal ParentingTip
    dp.register_message_handler(add_new_article, commands=['new'], state='*')
    dp.register_message_handler(set_header, state=Article.header.state)
    dp.register_message_handler(set_body, state=Article.tip.state)
    dp.register_message_handler(set_tags, state=Article.tags.state)
    dp.register_callback_query_handler(set_age_inline, cb.filter(), state=Article.age_range.state)

    # States for creating DailyTip
    dp.register_message_handler(add_new_daily_article, commands=['new_daily'], state='*')
    dp.register_message_handler(header_input, state=DailyArticle.header)
    dp.register_message_handler(body_input, state=DailyArticle.body)
    dp.register_message_handler(age_in_days_input, state=DailyArticle.age_in_days)
    dp.register_message_handler(pass_media, commands=['media_pass'], state=DailyArticle.media)
    dp.register_message_handler(add_media_for_daily_tip, content_types=['photo'], state=DailyArticle.media)

