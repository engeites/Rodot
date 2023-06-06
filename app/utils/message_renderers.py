from datetime import datetime

from app.database import tips_crud, ads_crud
from app.database.advice_crud import get_advice_for_age
from app.database.models import User, Child, ParentingTip
from app.extentions import logger
from app.utils.validators import calculate_age_in_days
from app.texts.profile_texts import my_child, my_child_not_born

class MyChildMessageRenderer:
    """
    This class is used to form final message text when Мой ребёнок is chosen in Profile menu
    """
    sex_options = {
        'male': 'мальчик',
        'female': 'девочка',
        'unknown': 'неизвестно'
    }

    def __init__(self, user: User):
        logger.info(f"Created MyChildMessageRenderer to send info to user {user.telegram_user_id}")
        self.user = user

    def get_readable_date(self, birth_date: datetime) -> str:
        return birth_date.strftime("%d.%m.%Y")

    def get_user_child(self) -> Child|bool:
        # TODO: This func may return None
        try:
            children: list = self.user.children
            return children[0]
        except Exception as e:
            return False


    def form_advice_text(self):
        advices: tuple = get_advice_for_age(calculate_age_in_days(self.get_user_child().age))
        if not advices:
            return "❤️ Пока ничего нового"

        advice_addon = ""

        for advice in advices:
            advice_addon += f"❤️ {advice.advice}\n"

        return advice_addon

    def check_if_born(self, date_obj: datetime) -> str:
        """
        This function determines if a date set as baby's birthday is in past or in the future
        :param date_obj: birth_date of Child from db
        :return: str "born" if user was born, "not born" if user is yet to be born
        """
        if date_obj < datetime.now():
            return "born"
        else:
            return "not born"

    def form_child_not_born_message(self):
        text = my_child_not_born.format(
            self.form_advice_text()
        )

        return text

    def form_my_child_message(self, child: Child):
        age_in_days = calculate_age_in_days(child.age)
        last_digit = int(str(age_in_days)[-1])

        if last_digit in [0, 5, 6, 7, 8, 9]:
            cor_date = "дней"
        elif last_digit in [2, 3, 4]:
            cor_date = "дня"
        else:
            cor_date = "день"

        text = my_child.format(
            self.get_readable_date(child.age),
            age_in_days,
            cor_date,
            self.sex_options[child.sex],
            self.form_advice_text()
        )
        return text

    def form_final_message(self):
        child = self.get_user_child()
        if not child:
            return "Вы не добавляли данных о своём ребёнке"
        if self.check_if_born(child.age) == "born":
            return self.form_my_child_message(child)
        else:
            return self.form_child_not_born_message()


class TipRenderer:
    def __init__(self, tip: ParentingTip):
        logger.info("Created ParentingTip renderer")
        self.tip = tip

    def add_advertisement_text(self):
        if self.tip.advertisement:
            logger.info(f"Ad from tip: {self.tip.header} was shown")

            ads_crud.add_advertisement_log(self.tip.id)
            return f"\n\n#ad\n{self.tip.advertisement.name}"
        return False


    def form_final_text(self):
        text = ""

        text += f"<b>{self.tip.header}</b> \n\n"
        text += self.tip.tip

        ad_text = self.add_advertisement_text()

        if not ad_text:
            logger.info(f"Rendered tip {self.tip.header}. Tip has no ads at moment")
            return text

        logger.info(f"Rendered tip {self.tip.header}. Tip has ad text")
        text += ad_text
        return text




