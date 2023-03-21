from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from app.database import user_crud, tips_crud
from app.database.models import ParentingTip


cb = CallbackData("bookmark", "tip_id")
bookmark_link_cb = CallbackData('link_to_tip', 'tip_id')

def add_bookmark_keyboard(tip_id):
    mark = InlineKeyboardMarkup()

    add_bookmark = InlineKeyboardButton(
        text="Добавить в сохранённые",
        callback_data=cb.new(tip_id=tip_id)
    )
    go_to_main = InlineKeyboardButton(
        text="Назад",
        callback_data="Назад"
    )

    mark.add(add_bookmark, go_to_main)
    return mark


def all_bookmarks_keyboard(user_id: int):
    # TODO: I think that it might be a bad idea to use database crud
    #   operations in file that describes keyboard. Maybe need to move query
    #   and pass needed objects to this function

    mark = InlineKeyboardMarkup()
    bookmarks = user_crud.get_my_bookmarks(user_id)

    tip_id_list = []
    if len(tip_id_list) == 0:
        return False
    for bookmark in bookmarks:
        tip_id_list.append(bookmark.bookmarked_tip_id)

    # TODO: Here I get whole Tip object but only use ID and header.
    #   Think of rewriting it to only query needed columns
    tips: list[ParentingTip] = tips_crud.get_multiple_tips_by_ids(tip_id_list)

    for tip in tips:
        mark.add(InlineKeyboardButton(
            text = tip.header,
            callback_data=bookmark_link_cb.new(tip_id=tip.id)
        ))

    return mark