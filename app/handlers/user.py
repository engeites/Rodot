import asyncio
from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text

from app.keyboards.main_keyboards import categories_keyboard
from app.keyboards.profile import profile_keyboard

from aiogram.utils.exceptions import BotBlocked



async def profile_menu(message: types.Message):
    await message.answer(
        "Welcome to profile menu. Here you can make your work with me much easier! "
        "I highly recommend to fill in some information about the baby and yourself, so I can give you right what "
        "you need.",
        reply_markup=profile_keyboard()
    )


async def main_menu(message: types.Message):
    await message.answer(
        "Welcome to main menu",
        reply_markup=categories_keyboard()
    )

async def bad_tips(message: types.Message):
    text = """Parental advice has been passed down from generation to generation for centuries. However, it is not always reliable or even safe. Many pieces of advice that were once considered effective and safe may now be outdated or even dangerous. In some cases, following such advice can even be lethal.
For instance, some older generations may suggest that putting butter or oil on a burn will soothe the pain and promote healing. However, this is not only ineffective but can even cause further damage to the skin. Another example is the idea that a baby should be put to sleep on their stomach to prevent choking. This advice is now known to be dangerous and can increase the risk of sudden infant death syndrome (SIDS).
It is important to be aware that not all parental advice is based on scientific evidence or modern knowledge. When in doubt, it is best to seek advice from healthcare professionals who have up-to-date knowledge and training. While respecting the wisdom of previous generations, we must always ensure the safety and wellbeing of our children.\n\n
"""
    text += "Here are some examples of bad advice like this:\n\n"
    text += """
Put some whiskey on the baby's gums to soothe teething pain.
Leave the baby to "cry it out" so that they learn to self-soothe.
Put rice cereal in the baby's bottle to help them sleep through the night.
Let the baby sleep on their stomach to prevent them from choking on spit-up.
Clean the baby's umbilical cord with alcohol several times a day.
Use baby powder to prevent diaper rash.
Give the baby a little bit of honey to soothe a cough or sore throat.
Wrap the baby tightly in blankets to prevent them from moving too much in their sleep.
Put a little bit of Karo syrup in the baby's bottle to relieve constipation.
Wake the baby up every two hours to feed them, even if they are sleeping soundly.
Rub brandy on the baby's gums to reduce fever.
Feed the baby solids before six months old to help them sleep better at night"""
    await message.answer(text)


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
    dp.register_message_handler(profile_menu, Text(equals="My Profile"))
    dp.register_message_handler(main_menu, Text(equals="Go to main menu"))
    dp.register_message_handler(bad_tips, Text(equals="Bad Tips"))