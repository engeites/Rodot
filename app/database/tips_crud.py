from datetime import datetime

from sqlalchemy.orm import sessionmaker, subqueryload, joinedload
from sqlalchemy import or_
from typing import List
from .models import ParentingTip
from .db import engine


Session = sessionmaker(bind=engine)


def create_new_article(article_data: dict, from_day: int, until_day: int) -> ParentingTip:
    db = Session()
    current_date = datetime.now()

    tip_header = article_data['header']
    tip_body = article_data['tip']
    tip_category = article_data['category']

    tip = ParentingTip(
        header=tip_header,
        tip=tip_body,
        category=tip_category,
        age_in_days=0,
        useful_from_day=from_day,
        useful_until_day=until_day,
        created_at=current_date
    )

    db.add(tip)
    db.commit()
    db.refresh(tip)
    return tip

def create_new_article_old(article_data: dict, from_day: int, until_day: int):
    db = Session()
    current_date = datetime.now()

    tip_header = article_data['header']
    tip_body = article_data['tip']

    tip = ParentingTip(
        header=tip_header,
        tip=tip_body,
        age_in_days=0,
        useful_from_day=from_day,
        useful_until_day=until_day,
        created_at=current_date
    )
    # tag_list = get_tags_from_str(article_data['tags'])

    # for tag_name in tag_list:
    #     tag = Tag(name=tag_name.strip())
    #     tip.tags.append(tag)
    #     db.add(tag)
    db.add(tip)
    db.commit()
    db.refresh(tip)
    return tip


def get_multiple_tips_by_ids(id_list: list):
    session = Session()
    tips = session.query(ParentingTip).filter(ParentingTip.id.in_(id_list)).all()
    session.close()
    return tips


def get_tip_by_id(tip_id: int) -> ParentingTip:
    session = Session()
    try:
        parenting_tip = session.query(ParentingTip).options(joinedload(ParentingTip.advertisement)).get(tip_id)
        return parenting_tip
    finally:
        session.close()


def update_tip_text(tip_id: int, new_text: str):
    session = Session()
    session.query(ParentingTip).filter(ParentingTip.id == tip_id).update(
        {ParentingTip.tip: new_text},
        synchronize_session=False
    )
    session.commit()


def delete_parenting_tip(tip_id: int):
    session = Session()
    tip = session.query(ParentingTip).get(tip_id)
    if tip:
        session.delete(tip)
        session.commit()


def get_tips_by_category(category: str, start_age: int=1, end_age: int=540) -> list:
    session = Session()

    tip_list = session.query(ParentingTip).filter(
        ParentingTip.category == category,
        ParentingTip.useful_from_day == start_age,
        ParentingTip.useful_until_day == end_age,
    )
    session.close()
    return tip_list

def get_all_tips() -> List[ParentingTip]:
    session = Session()
    tips = session.query(ParentingTip).all()
    session.close()
    return tips


def search_tips_by_query(query_txt: str) -> list:
    session = Session()

    # split query into individual keywords
    keywords = query_txt.split()

    # create a list of filter conditions to search for each keyword
    filter_conditions = [ParentingTip.tip.like(f'%{keyword}%') for keyword in keywords]

    # combine the filter conditions with an OR operator
    combined_filter = or_(*filter_conditions)

    # query the database for articles matching the filter conditions
    articles = session.query(ParentingTip).filter(combined_filter).all()

    return articles


def get_tip_with_media(tip_id: int):
    db = Session()
   # the ID of the ParentingTip you want to retrieve
    tip_with_media = db.session.query(ParentingTip).options(subqueryload(ParentingTip.media)).filter_by(
        id=tip_id).first()
    
    return tip_with_media


def update_tip(tip_id: int, age_in_months: int, tip_text: str) -> ParentingTip:
    session = Session()
    tip = session.query(ParentingTip).filter(ParentingTip.id == tip_id).first()
    tip.age_range = age_in_months
    tip.tip_text = tip_text
    session.commit()
    session.refresh(tip)
    session.close()
    return tip

def delete_tip(tip_id: int) -> None:
    session = Session()
    tip = session.query(ParentingTip).filter(ParentingTip.id == tip_id).first()
    session.delete(tip)
    session.commit()
    session.close()
