from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text, Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery

profile_btns = ['Мой город', 'Мой ребёнок', 'Сохраненные статьи']
age_btns = ['новорожденным', 'подросшим', 'подросшим ещё', 'совсем большим', 'back']

prof_button_list = [InlineKeyboardButton(text=name, callback_data=name) for name in profile_btns]
prof_kb = InlineKeyboardMarkup(row_width=2)
prof_kb.add(*prof_button_list)

age_button_list = [InlineKeyboardButton(text=name, callback_data=name) for name in age_btns]
age_kb = InlineKeyboardMarkup(row_width=2)
age_kb.add(*age_button_list)


async def show_inline_profile_kb(message: types.Message):
    await message.answer("Выбери мой город", reply_markup=prof_kb)


async def my_city(call: CallbackQuery):
    await call.message.edit_text('Ты выбрал мой город, хахах', reply_markup=age_kb)
    await call.answer('Вот я отвечаю')



async def go_back(call: CallbackQuery):
    await call.message.edit_text("Вернулись на главную. Снова выбери мой город", reply_markup=prof_kb)


def register_test_handlers(dp: Dispatcher):
    dp.register_message_handler(show_inline_profile_kb, commands=['test'])
    dp.register_callback_query_handler(my_city, Text(equals="🏙 Мой город"))
    dp.register_callback_query_handler(go_back, Text(equals="back"))
