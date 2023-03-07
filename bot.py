from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text

from keyboards.main_keyboard import create_main_keyboard
from main import get_users
from handlers.user import callback_data
from handlers.user import send_welcome, callbacks, newborn_care_intro, cmd_random, \
    send_random_number, profile_menu, main_menu, bad_tips

from config import API_TOKEN

def create_bot():
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot)

    dp.register_message_handler(send_welcome, commands=['start'])
    dp.register_message_handler(cmd_random, commands=['random'])
    dp.register_message_handler(newborn_care_intro, Text(equals="Newborn Care"))
    dp.register_callback_query_handler(send_random_number, Text(equals="random_value"))
    dp.register_callback_query_handler(callbacks, callback_data.filter())
    dp.register_message_handler(profile_menu, Text(equals="My Profile"))
    dp.register_message_handler(main_menu, Text(equals="Go to main menu"))
    dp.register_message_handler(bad_tips, Text(equals="Bad Tips"))
    return bot, dp


if __name__ == '__main__':
    bot, dp = create_bot()
    executor.start_polling(dp, skip_updates=True)
