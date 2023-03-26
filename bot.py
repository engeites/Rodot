import asyncio
import logging

from aiogram import types
from aiogram.dispatcher.webhook import SendMessage
from aiohttp import web

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.handlers.registration import register_registry_handlers
from app.handlers.update_profile import register_update_info_handlers
from app.handlers.basic import register_basic_handlers
from app.handlers.articles import register_articles_handlers
from app.handlers.admin import register_admin_hanlders
from app.handlers.profile import register_profile_handlers
from app.handlers.user import register_user_handlers
from app.handlers.test import  register_test_handlers

from app.config import API_TOKEN

logger = logging.getLogger(__name__)

WEBHOOK_HOST = '127.0.0.1'
WEBHOOK_PATH = '/my_webhook_path'

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
    register_update_info_handlers(dp)
    register_registry_handlers(dp)
    register_articles_handlers(dp)
    register_basic_handlers(dp)
    await dp.start_polling()


def create_webhook_bot():
    # Replace 'API_TOKEN' with your own bot token obtained from BotFather
    bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)

    async def on_startup(app):
        # Replace 'WEBHOOK_HOST' with your own hostname or IP address
        await bot.set_webhook(f'https://WEBHOOK_HOST/{WEBHOOK_PATH}')

    async def on_shutdown(app):
        # Remove webhook upon shutdown
        await bot.delete_webhook()

    async def webhook(request):
        if request.match_info.get('token') == API_TOKEN:
            update = await request.json()
            # Process update here
            await dp.process_update(update)
            return web.Response(text='OK')
        return web.Response(text='Invalid token')

    app = web.Application()
    # Replace 'WEBHOOK_PATH' with your own webhook path
    app.router.add_post(f'/token:{API_TOKEN}/{WEBHOOK_PATH}', webhook)

    web.run_app(app, host=WEBHOOK_HOST, port=8443)

if __name__ == '__main__':
    create_webhook_bot()







#
# if __name__ == '__main__':
#     # create_webhook_bot()
#     # asyncio.run(create_bot())
