from random import randint

from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.callback_data import CallbackData

from app.keyboards.main_keyboard import create_main_keyboard
from app.keyboards.profile import profile_keyboard
from app.database.tips_crud import get_all_tips, get_tip_by_id

from utils.form_newborn_contents import newborn_section_introduction


async def send_welcome(message: types.Message):
    text = """
    Hello and welcome to the Parenting Tips bot! 

I'm here to help you navigate the challenges of parenting and provide you with valuable information and advice for your child's development. 

To get started, please select a category from the menu below:
- Newborn Care
- Sleeping Tips
- Feeding Advice
- Developmental Activities
- And more!

You can also search for articles by typing a keyword or topic in the search bar. 

Thank you for using Parenting Tips bot, and happy parenting! 
"""
    await message.answer(text, reply_markup=create_main_keyboard())


# async def return_newborn_care_contents(message: types.Message):
    # text = utils.form_newborn_contents.get_tips_with_tag('newborn')
    # await message.answer(text, reply_markup=create_main_keyboard())


async def cmd_random(message: types.Message):
    mark = InlineKeyboardMarkup()
    mark.add(InlineKeyboardButton(
        text="Нажми меня",
        callback_data="random_value")
    )

    await message.answer(
        "Нажмите на кнопку, чтобы бот отправил число от 1 до 10",
        reply_markup=mark
    )

async def send_random_number(callback: types.CallbackQuery):
    await callback.message.answer(str(randint(1, 10)))
    await callback.answer(
        text="Спасибо, что воспользовались ботом!",
        show_alert=True
    )


callback_data = CallbackData('articles', 'id')


async def newborn_care_intro(message: types.Message):
    mark = InlineKeyboardMarkup()

    tips = get_all_tips()
    for tip in tips:
        mark.add(InlineKeyboardButton(
            text=tip.header,
            callback_data=callback_data.new(str(tip.id))
        ))

    await message.answer(newborn_section_introduction(), reply_markup=mark)

async def callbacks(call: types.CallbackQuery, callback_data: dict):
    post_id = callback_data["id"]
    await call.message.answer(get_tip_by_id(post_id).tip)


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
        reply_markup=create_main_keyboard()
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