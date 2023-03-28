from aiogram import types, Dispatcher
from aiogram.utils.exceptions import BotBlocked



async def error_bot_blocked(update: types.Update, exception: BotBlocked):
    # TODO: Придумать и добавить обработку ботом блокировки
    # Update: объект события от Telegram. Exception: объект исключения
    # Здесь можно как-то обработать блокировку, например, удалить пользователя из БД
    print(f"Меня заблокировал пользователь!\nСообщение: {update}\nОшибка: {exception}")

    # Такой хэндлер должен всегда возвращать True,
    # если дальнейшая обработка не требуется.
    return True



def register_user_handlers(dp: Dispatcher):
    dp.register_errors_handler(error_bot_blocked, exception=BotBlocked)