from datetime import datetime, timedelta
from typing import List

import aiogram
from sqlalchemy import func
from sqlalchemy.orm import sessionmaker, joinedload
from app.database.models import DailyTip, Child, User, tags_association_table

from .db import engine

Session = sessionmaker(bind=engine)

async def send_daily_tips(bot: aiogram.Bot):
    print('Send daily tips ran')
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