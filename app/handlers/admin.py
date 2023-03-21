from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

from app.utils.validators import validate_age
from app.database.tips_crud import create_new_article

from app.keyboards.inline.ages import ages_keyboard, cb

class Article(StatesGroup):
    header = State()
    tip = State()
    tags = State()
    age_in_days = State()


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
    await state.set_state(Article.age_in_days.state)
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

async def set_age(message: types.Message, state: FSMContext):
    age = message.text

    # Validate if int
    age_valid = validate_age(age)

    if not age_valid:
        await message.answer("Age is not valid. Please input age in days")
        return

    article_data = await state.get_data()
    article_data['age_in_days'] = age_valid

    success = create_new_article(article_data)
    if not success:
        await message.answer("Something went wrong. Article was not saved")
        return

    await state.finish()
    await message.answer("New article is successfully saved")


def register_admin_hanlders(dp: Dispatcher):
    dp.register_message_handler(add_new_article, commands=['new'], state='*')
    dp.register_message_handler(set_header, state=Article.header.state)
    dp.register_message_handler(set_body, state=Article.tip.state)
    dp.register_message_handler(set_tags, state=Article.tags.state)
    # dp.register_message_handler(set_age, state=Article.age_in_days.state)
    dp.register_callback_query_handler(set_age_inline, cb.filter(), state=Article.age_in_days.state)