from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.database import tips_crud
from app.database.models import ParentingTip
from app.handlers.articles import callback_data


def form_tip_list(data: dict) -> InlineKeyboardMarkup:
    print(data)
    tips: list[ParentingTip] = tips_crud.get_tips_by_multiple_tags(data['category'],
                                                                   int(data['from_day']),
                                                                   int(data['until_day']))

    mark = InlineKeyboardMarkup()

    for tip in tips:
        mark.add(InlineKeyboardButton(
            text=tip.header,
            callback_data=callback_data.new(str(tip.id))
        ))

    mark.add(InlineKeyboardButton(
        text="< Назад",
        callback_data="< Назад"
    ),
        InlineKeyboardButton(
            text="На главную",
            callback_data="На главную"
        ))

    return mark
