from datetime import datetime

from sqlalchemy.orm import sessionmaker, subqueryload
from sqlalchemy import or_
from sqlalchemy.sql import text, func, and_
from typing import List
from .models import ParentingTip, Tag
from .db import engine

from app.utils.validators import get_tags_from_str

Session = sessionmaker(bind=engine)


def create_tip(header: str, tip_text: str, tag_names: List[str], age_in_days: int):
    db = Session()
    tip = ParentingTip(age_in_days=age_in_days, header=header, tip=tip_text)
    for tag_name in tag_names:
        tag = Tag(name=tag_name)
        tip.tags.append(tag)
        db.add(tag)
    db.add(tip)
    db.commit()
    db.refresh(tip)
    return tip

def create_new_article(article_data: dict, from_day: int, until_day: int):
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
    tag_list = get_tags_from_str(article_data['tags'])

    for tag_name in tag_list:
        tag = Tag(name=tag_name.strip())
        tip.tags.append(tag)
        db.add(tag)
    db.add(tip)
    db.commit()
    db.refresh(tip)
    return tip


def get_multiple_tips_by_ids(id_list: list):
    session = Session()
    print(f"Got these id's: {id_list}")
    tips = session.query(ParentingTip).filter(ParentingTip.id.in_(id_list)).all()
    for tip in tips:
        print(tip)
    session.close()
    return tips

def get_tip_by_id(tip_id: int) -> ParentingTip:
    session = Session()
    tip = session.query(ParentingTip).filter(ParentingTip.id == tip_id).first()
    session.close()
    return tip


def get_all_tips() -> List[ParentingTip]:
    session = Session()
    tips = session.query(ParentingTip).all()
    session.close()
    return tips


def get_tips_by_multiple_tags(tags_list: list, start_age=1, end_age=540):
    session = Session()
    print(tags_list)

    query = session.query(ParentingTip). \
        join(ParentingTip.tags). \
        filter(Tag.name.in_(tags_list)). \
        filter(and_(ParentingTip.useful_from_day >= start_age, ParentingTip.useful_until_day <= end_age)). \
        distinct(ParentingTip.id)

    tips_by_tags = query.all()
    return tips_by_tags

def search_tips(query_txt):
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

def get_tips_by_tag(tag: str):
    db = Session()
    # print(f"Looking for tag: '{tag}' of type {type(tag)} ")
    # tips = db.query(ParentingTip).filter(ParentingTip.tags.any(tag)).all()
    # tag_expr = text(tag)
    tag_expr = text(f"'{tag}'")
    # test = db.query(ParentingTip)
    # for i in test:
    #     for j in i.tags:
    #         print(j.name)
    # tips = db.query(ParentingTip).filter(ParentingTip.tags.any(tag) == tag_expr).all()
    # tips = db.query(ParentingTip).filter(ParentingTip.tags.any(tag) == True).all()
    # tips = db.query(ParentingTip).filter(ParentingTip.tags.any(tag_expr)).all()
    # tips = (
    #     db.query(ParentingTip)
    #     .join(ParentingTip.tags)
    #     .filter(Tag.name == tag_expr)
    #     .all()
    # )

    # tips = db.query(ParentingTip).filter(ParentingTip.tags.any(Tag.name == tag_expr)).all()

    tips = db.query(ParentingTip).join(ParentingTip.tags).filter(Tag.name == tag_expr).all()

    return tips


def update_tip(tip_id: int, age_in_months: int, tip_text: str) -> ParentingTip:
    session = Session()
    tip = session.query(ParentingTip).filter(ParentingTip.id == tip_id).first()
    tip.age_in_days = age_in_months
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
