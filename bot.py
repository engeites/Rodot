import asyncio
import logging


from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.handlers.registration import register_registry_handlers
from app.handlers.update_profile import register_info_handlers
from app.handlers.basic import register_basic_handlers
from app.handlers.articles import register_articles_handlers
from app.handlers.admin import register_admin_hanlders
from app.handlers.profile import register_profile_handlers
from app.handlers.user import register_user_handlers
from app.handlers.test import  register_test_handlers

from app.config import API_TOKEN

logger = logging.getLogger(__name__)

async def create_bot():

    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    bot = Bot(token=API_TOKEN, parse_mode='HTML')
    dp = Dispatcher(bot, storage=MemoryStorage())

    # register_test_handlers(dp)
    register_admin_hanlders(dp)
    register_user_handlers(dp)
    register_profile_handlers(dp)
    register_info_handlers(dp)
    register_registry_handlers(dp)
    register_articles_handlers(dp)
    register_basic_handlers(dp)
    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(create_bot())
