import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text

from app.handlers.callback import callback_data
from app.handlers.registration import register_profile_handlers
from app.handlers.update_profile import register_info_handlers
from app.handlers.basic import register_basic_handlers
from app.handlers.admin import register_admin_hanlders
from app.handlers.profile import register_profile_handlers

from app.handlers.user import callbacks, newborn_care_intro, profile_menu, main_menu, bad_tips

from app.config import API_TOKEN

logger = logging.getLogger(__name__)

async def create_bot():

    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=MemoryStorage())

    # dp.register_message_handler(send_welcome, commands=['start'])
    # dp.register_message_handler(cmd_random, commands=['random'])
    dp.register_message_handler(newborn_care_intro, Text(equals="Newborn Care"))
    # dp.register_callback_query_handler(send_random_number, Text(equals="random_value"))
    dp.register_callback_query_handler(callbacks, callback_data.filter())
    dp.register_message_handler(profile_menu, Text(equals="My Profile"))
    dp.register_message_handler(main_menu, Text(equals="Go to main menu"))
    dp.register_message_handler(bad_tips, Text(equals="Bad Tips"))

    register_profile_handlers(dp)
    register_profile_handlers(dp)
    register_info_handlers(dp)
    register_basic_handlers(dp)
    register_admin_hanlders(dp)

    await dp.start_polling()



if __name__ == '__main__':
    asyncio.run(create_bot())
