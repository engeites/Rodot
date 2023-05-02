import asyncio
import logging

from app.database.daily_tips import send_daily_tips_to_all
from app.utils.apschedule import scheduler, job_timezone, job_time

from aiogram import Bot, Dispatcher
from aiogram import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from app.handlers.registration import register_registry_handlers
from app.handlers.update_profile import register_update_info_handlers
from app.handlers.basic import register_basic_handlers
from app.handlers.articles import register_articles_handlers
from app.handlers.admin import register_admin_hanlders
from app.handlers.profile import register_profile_handlers
from app.handlers.errors import register_user_handlers
from app.handlers.prenatal import register_prenatal_handlers

from config import API_TOKEN
from app.database import user_crud
from app.middlewares.throttling import ThrottlingMiddleware
from app.middlewares.all_callbacks import BigBrother

from app.extentions import logger, ADMINS


async def create_bot():

    # Настройка логирования в stdout
    logging.basicConfig(
        level=logging.INFO,
        filename='rodot.log',
        filemode='a',
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logger.error("Starting bot")

    logger.info(f"list of admins: {ADMINS}")

    bot = Bot(token=API_TOKEN, parse_mode='HTML')
    dp = Dispatcher(bot, storage=MemoryStorage())

    dp.middleware.setup(BigBrother())
    dp.middleware.setup(ThrottlingMiddleware())

    register_admin_hanlders(dp)

    register_user_handlers(dp)
    register_prenatal_handlers(dp)
    register_basic_handlers(dp)

    register_profile_handlers(dp)
    register_update_info_handlers(dp)
    register_registry_handlers(dp)
    register_articles_handlers(dp)


    scheduler.add_job(send_daily_tips_to_all, 'cron', day_of_week='mon-sun', hour=job_time.hour, minute=job_time.minute,
                      timezone=job_timezone, args=[bot])
    # scheduler.add_job(send_daily_tips_to_all, 'interval', minutes=1, args=[bot])
    scheduler.start()
    await dp.start_polling(timeout=600)



if __name__ == '__main__':
    asyncio.run(create_bot())






#
# if __name__ == '__main__':
#     # create_webhook_bot()
#     # asyncio.run(create_bot())
