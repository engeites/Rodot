from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.config import AVAILABLE_AGES_initial
cb = CallbackData("get_age", "from_day", "until_day")

def ages_keyboard():
    mark = InlineKeyboardMarkup()

    age_buttons = [InlineKeyboardButton(text=age[0],
                                        callback_data=cb.new(
                                            from_day=age[1],
                                            until_day=age[2])
                                        )

               for age in AVAILABLE_AGES_initial]

    cancel = InlineKeyboardButton(text="На главную", callback_data=cb.new(
        from_day='back',
        until_day='back')
    )

    mark.add(*age_buttons)
    mark.add(cancel)

    return mark

ages_keyboard = ages_keyboard()
#
# def ages_keyboard():
#     mark = InlineKeyboardMarkup()
#
#     newborn = InlineKeyboardButton(
#         text="Новорожденным",
#         callback_data=cb.new(from_day="0", until_day="0")
#     )
#     from_0_to_3 = InlineKeyboardButton(
#         text="0-3 месяца",
#         callback_data=cb.new(from_day="1", until_day="90")
#     )
#
#     from_3_to_6 = InlineKeyboardButton(
#         text="3-6 месяцев",
#         callback_data=cb.new(from_day="91", until_day="180")
#     )
#
#     from_6_to_9 = InlineKeyboardButton(
#         text="6-9 месяцев",
#         callback_data=cb.new(from_day="181", until_day="270")
#     )
#
#     from_9_to_12 = InlineKeyboardButton(
#         text="9-12 месяцев",
#         callback_data=cb.new(from_day="271", until_day="360")
#     )
#
#     from_12_to_15 = InlineKeyboardButton(
#         text="12-15 месяцев",
#         callback_data=cb.new(from_day="361", until_day="450")
#     )
#
#     from_15_to_18 = InlineKeyboardButton(
#         text="15-18 месяцев",
#         callback_data=cb.new(from_day="451", until_day="540")
#     )
#
#     cancel = InlineKeyboardButton(
#         text="На главную",
#         callback_data=cb.new(from_day="back", until_day="back")
#     )
#
#     mark.add(newborn, from_0_to_3).add(from_3_to_6, from_6_to_9).add(from_9_to_12, from_12_to_15).add(from_15_to_18, cancel)
#     return mark

