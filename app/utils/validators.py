import datetime
from datetime import datetime
from typing import List

def validate_city(given_city: str) -> str | bool:
    options = ["moscow", "saint petersburg", "rostov", "stavropol", "omsk", "tomsk", "pyatigorsk"]
    if given_city.lower() not in options:
        return False
    return given_city


def validate_age(age: str) -> int | bool:
    try:
        valid_age = int(age)
        return valid_age
    except ValueError:
        return False


def get_tags_from_str(tags: str) -> List[str]:
    tag_list = tags.split(',')
    return tag_list


def calculate_age_in_days(birth_date: datetime) -> int:
    today = datetime.now()
    delta = today - birth_date
    num_days = delta.days
    return num_days