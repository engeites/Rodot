from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware, BaseMiddleware
from aiogram import types
from app.config import BANNED_USERS
from aiogram.dispatcher.storage import FSMContext

class BigBrother(BaseMiddleware):
    async def on_pre_process_update(self, update: types.Update, data: dict):
        if update.message:
            user_id = update.message.from_user.id
        elif update.callback_query:
            user_id = update.callback_query.from_user.id
        else:
            return


        if user_id in BANNED_USERS:
            raise CancelHandler()


    # async def on_process_update(self, update: types.Update, data: dict):
    #     pass
    #
    # async def on_pre_process_message(self, message: types.Message, data: dict):
    #     pass
    #
    # async def on_post_process_message(self, message: types.Message, data_from_handler: list, data: dict):
    #     pass
