from datetime import datetime

from app.database import tips_crud, user_crud


def get_current_time():
    return datetime.now()


def create_new_user():
    telegram_chat_id = "875321240-6"
    telegram_user_id = "Alex"
    created_time = get_current_time()
    user_crud.create_user(telegram_user_id, telegram_chat_id, created_time)


def get_users():
    return user_crud.get_all_users()
    # for i in users:
    #     print(i.telegram_chat_id, i.telegram_user_id, i.created_at)


def create_new_tip():
    age = 1
    tip_text = """
    Newborn crying can be distressing for both the baby and the parents. However, it is a normal part of their development and communication. Babies cry for various reasons, including hunger, discomfort, tiredness, or just to express their needs. Soothing techniques like holding, swaying, or gentle rocking can be helpful. Other methods like white noise, pacifiers, or skin-to-skin contact can also provide comfort. It is essential to understand that it is normal for babies to cry, and it is okay to ask for help if needed. With time and patience, parents can learn to soothe their baby and strengthen their bond
    """
    tip_header = "newborn soothing"
    tags = ["soothing", "parenting"]
    tips_crud.create_tip(age, tip_header, tip_text, tags)


def get_tips():
    tips = tips_crud.get_all_tips()
    for tip in tips:
        print(tip.header + "\n")
        print(tip.tip + "\n")
        print(f"This was the tip for babies of {tip.age_in_days} days old with tags: {[tag.name for tag in tip.tags]}")


def get_tips_by_tag(tag):
    tips = tips_crud.get_tips_by_tag(tag)
    print("HERE ARE THE TIPS: \n" + "-"*30)
    print(tips)



if __name__ == '__main__':
    # create_new_user()
    # get_users()
    # create_new_tip()
    # get_tips()
    get_tips_by_tag("newborn_care")