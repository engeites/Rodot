import datetime
from datetime import datetime
from typing import List

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
            pass

    return False


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
    print(f'got this: {birth_date}')
    today = datetime.now()
    delta = today - birth_date
    num_days = delta.days
    return num_days


def calc_age_range_from_int(age_in_days: int) -> dict:
    if 1 <= age_in_days <= 30:
        return {'start': 1, 'end': 30}
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