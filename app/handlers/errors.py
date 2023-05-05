from aiogram import types, Dispatcher
from aiogram.utils.exceptions import BotBlocked

from app.database import user_crud
from app.extentions import logger


async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    # print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

    user_crud.mark_user_that_blocked_bot(update.message.from_user.id)
    logger.info(f"User {update.message.from_user.id} has blocked the bot")
    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True



def register_user_handlers(dp: Dispatcher):
    dp.register_errors_handler(error_bot_blocked, exception=BotBlocked)