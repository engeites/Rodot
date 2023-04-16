from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def create_confirm_subscription_kb():
    confirm = InlineKeyboardButton(text="Да", callback_data='confirm_subscription')
    cancel = InlineKeyboardButton(text="Нет", callback_data='cancel_subscription')

    return InlineKeyboardMarkup().add(confirm, cancel)

confirm_subscription_kb = create_confirm_subscription_kb()