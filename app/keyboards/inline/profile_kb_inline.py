
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import PROFILE_KB_BTNS


# Create a list of InlineKeyboardButton objects
buttons = [InlineKeyboardButton(text=name, callback_data=name) for name in PROFILE_KB_BTNS]

# Create an InlineKeyboardMarkup object with the list of buttons
profile_kb = InlineKeyboardMarkup(row_width=2)
profile_kb.add(*buttons)

