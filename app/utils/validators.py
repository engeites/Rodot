import datetime
from datetime import datetime, timedelta, timezone
from typing import List

from app.extentions import logger


def validate_city(given_city: str) -> str | bool:
    options = ["moscow", "saint petersburg", "rostov", "stavropol", "omsk", "tomsk", "pyatigorsk"]
    if given_city.lower() not in options:
        return False
    return given_city


def validate_date(date: str) -> datetime | bool:
    formats = ('%d.%m.%Y', '%m.%d.%Y', '%d-%m-%Y', '%m-%d-%Y')

    for format in formats:
        try:
            date_obj = datetime.strptime(date, format)
            return date_obj
        except ValueError:
            return False


def check_if_born(date_obj: datetime) -> str:
    if date_obj < datetime.now():
        return 'past'
    else:
        return 'future'

def validate_age(age: str) -> int | bool:
    try:
        valid_age = int(age)
        return valid_age
    except ValueError:
        return False


def get_tags_from_str(tags: str) -> List[str]:
    tag_list = tags.split(',')
    return tag_list


def add_days_to_today_utc(days):
    now = datetime.utcnow()
    future = now + timedelta(days=days)
    return future.replace(tzinfo=timezone.utc)


def calculate_age_in_days(birth_date: datetime) -> int:
    today = datetime.now()
    delta = today - birth_date
    num_days = delta.days
    logger.info(f"Calculating age in days for birthdate: {birth_date}. Got {num_days}")

    return num_days

def calc_age_range_from_int(age_in_days: int) -> dict:
    if age_in_days < -100:
        logger.warning(f"User tried to get categories for baby that is yet to be born. age_in_days={age_in_days}")
        return {'error': 'not born'}
    if -100 <= age_in_days < 0:
        return {'start': 0, 'end': 0}
    elif 0 <= age_in_days <= 30:
        return {'start': 0, 'end': 30}
    elif 31 <= age_in_days <= 180:
        return {'start': 31, 'end': 180}
    elif 181 <= age_in_days <= 165:
        return {'start': 181, 'end': 365}
    else:
        logger.warning(f"User tried to get categories for baby that is too old. age_in_days={age_in_days}")
        return {'error': 'too old'}


def calc_age_range_from_int_old(age_in_days: int) -> dict:
    # TODO: Return different results if a child is too old or yet to be born more that 100 days after

    if -100 <= age_in_days < 0:
        return {'start': 0, 'end': 0}
    if 0 <= age_in_days <= 30:
        return {'start': 0, 'end': 30}
    elif 31 <= age_in_days <= 60:
        return {'start': 31, 'end': 60}
    elif 61 <= age_in_days <= 90:
        return {'start': 61, 'end': 90}
    elif 91 <= age_in_days <= 120:
        return {'start': 91, 'end': 120}
    elif 121 <= age_in_days <= 150:
        return {'start': 121, 'end': 150}
    elif 151 <= age_in_days <= 180:
        return {'start': 151, 'end': 180}
    else:
        return {'error': 'out of range'}


def validate_category(input_str: str) -> str:
    return input_str[2:].strip()