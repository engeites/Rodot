from datetime import datetime

from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text, func, and_
from typing import List
from .models import ParentingTip, Tag, tags_association_table
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

def create_new_article(article_data: dict):
    db = Session()
    current_date = datetime.now()

    tip_header = article_data['header']
    tip_body = article_data['tip']
    tip_age = int(article_data['age_in_days'])

    tip = ParentingTip(
        header=tip_header,
        tip=tip_body,
        age_in_days=tip_age,
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
    # This query adds usage of useful_from_day and useful_until_day
    query = session.query(ParentingTip). \
        join(ParentingTip.tags). \
        filter(Tag.name.in_(tags_list)). \
        filter(and_(ParentingTip.useful_from_day >= start_age, ParentingTip.useful_until_day <= end_age)). \
        group_by(ParentingTip.id). \
        having(func.count(Tag.id) == len(tags_list))
    #
    # query = session.query(ParentingTip). \
    #     join(ParentingTip.tags). \
    #     filter(Tag.name.in_(tags_list)). \
    #     group_by(ParentingTip.id). \
    #     having(func.count(Tag.id) == len(tags_list))
    print(f"looking for articles with tags: {tags_list}, for babies from {start_age} to {end_age} days old")

    tips_by_tags = query.all()
    return tips_by_tags


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
