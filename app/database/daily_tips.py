from datetime import datetime, timedelta
from typing import List

import aiogram
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, joinedload
from app.database.models import DailyTip, Child, User
from . import user_crud

from .db import engine
from ..utils.validators import calculate_age_in_days

Session = sessionmaker(bind=engine)

async def send_daily_tips_to_all(bot: aiogram.Bot):
    session = Session()

    today = datetime.now().date()
    daily_tips = session.query(DailyTip).all()

    for daily_tip in daily_tips:
        calculated_date = today - timedelta(days=daily_tip.age_in_days)

        # 2. Query for matching Children and their parent User
        children = session.query(Child).options(joinedload(Child.parent)).filter(
            func.date(Child.age) == calculated_date
        ).all()

        if len(children) == 0:
            pass

        # 3. Send the DailyTip message to each parent
        for child in children:
            print(f"This child needs {daily_tip.header}. As his birthday is at {child.age}")
            parent = child.parent
            final_message = f"<b>{daily_tip.header}</b>\n\n{daily_tip.body}"
            await bot.send_message(chat_id=parent.telegram_user_id, text=final_message, parse_mode='HTML')

    session.close()


def send_daily_tip_to_user(user_id: int):
    session = Session()
    user_child = user_crud.get_user_child(user_id)
    user_child_birthday = user_child[0]
    print(user_child, user_child_birthday)

    age_in_days = calculate_age_in_days(user_child_birthday)

    daily_tip = session.query(DailyTip).filter(DailyTip.age_in_days == age_in_days).first()
    print(daily_tip)
    return daily_tip
