from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData


def build_admin_kb():
    add_parenting_tip = InlineKeyboardButton("Добавить статью", callback_data="add_material")
    del_parenting_tip = InlineKeyboardButton("Удалить статью", callback_data="del_material")
    add_daily_tip = InlineKeyboardButton("Добавить короткую статью", callback_data="add_daily")
    del_daily_tip = InlineKeyboardButton("Удалить короткую статью", callback_data="del_daily")
    add_short_advice = InlineKeyboardButton("Добавить совет", callback_data="add_advice")
    del_short_advice = InlineKeyboardButton("Удалить совет", callback_data="del_advice")

    send_one_time_message = InlineKeyboardButton("Сообщение всем", callback_data="send_one_time_media")

    active_users_stat = InlineKeyboardButton("Активные пользователи", callback_data='active_users_statistics')
    registered_users_stat = InlineKeyboardButton("Статистика регистраций", callback_data='registered_users_statistics')
    ad_panel = InlineKeyboardButton("Управление рекламой", callback_data='ad_control_panel')
    back = InlineKeyboardButton("На главную", callback_data="На главную")


    mark = InlineKeyboardMarkup()
    mark.add(add_parenting_tip, del_parenting_tip)
    mark.add(add_daily_tip, del_daily_tip)
    mark.add(add_short_advice, del_short_advice)
    mark.add(ad_panel)
    mark.add(send_one_time_message)

    mark.add(active_users_stat, registered_users_stat)
    mark.add(back)
    return mark


def build_cancel_input_kb():
    return InlineKeyboardMarkup().add(InlineKeyboardButton("Отмена", callback_data="cancel"))

admin_kb = build_admin_kb()
cancel_kb = build_cancel_input_kb()