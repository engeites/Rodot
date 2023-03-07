from typing import List

import database.models
from database import tips_crud


def newborn_section_introduction():
    # articles: List[database.models.ParentingTip] = tips_crud.get_tips_by_tag(tag)
    text = """Bringing a newborn into the world can feel like a daunting and overwhelming task, but as a parent, you are already equipped with the most important tool - love. With our support and guidance, you can embrace the challenge of newborn care with confidence and grace. From feeding and changing to soothing and bonding, every moment spent caring for your precious little one is an opportunity to nurture and grow a lifelong connection. You are capable of providing your newborn with the love, care, and attention they need to thrive, and we are here to support you every step of the way. Remember, every parent has been in your shoes, and with a little help and encouragement, you can do this - and you will do it with love.\n\n"""
    text += "Here are some topics that might be useful for you:\n"
    # for topic in articles:
    #     text += topic.header + "\n"

    return text
