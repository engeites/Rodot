import os

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    print("found file")
    load_dotenv(dotenv_path)

API_TOKEN = os.environ.get('BOT_API')


CATEGORIES = [
    ['🧼 Здоровье и гигиена', "Здоровье и гигиена"],
    ['🤱🏼 Кормление', 'Кормление'],
    ['🛏 Сон и режим', 'Сон и режим'],
    ['🐤 Игры и развитие', 'Игры и развитие'],
    ['🧸 Книги и игрушки', 'Книги и игрушки'],
    ['🤬 Вредные советы', 'Вредные советы'],
    ['🛒 Полезные покупки', 'Полезные покупки']
]


CATEGORIES_callback = [
    'Здоровье и гигиена',
    'Кормление',
    'Сон и режим',
    'Игры и развитие',
    'Книги и игрушки',
    'Вредные советы',
    'Полезные покупки',
]

PRENATAL_CATEGORIES = [
    ['🤰 Подготовка к родам', 'Подготовка к родам'],
    ['🛒 Покупки к рождению малыша', 'Покупки к рождению малыша'],
    ['👨‍👩‍👦‍👦 Подготовка мамы и семьи', 'Подготовка мамы и семьи']
]

INITIAL_CHOICE = [
    ['📖 Заполнить профиль', 'Заполнить профиль'],
    ['🐾 Выбрать возраст', 'Выбрать возраст'],
    ['🧑🏻‍🎓 Как пользоваться ботом', 'Как пользоваться ботом']
]

MAIN_KB_UNREG_BTNS = [
    ['📖 Заполнить профиль', 'Заполнить профиль'],
    ['🐾 Выбрать возраст', 'Выбрать возраст'],
    ['Как пользоваться ботом', 'Как пользоваться ботом'],
    ['Связаться с нами', 'Связаться с нами']
]

PROFILE_KB_BTNS = [
    '👼🏻 Мой ребёнок',
    '🏙 Мой город',
    '📗 Сохранённые статьи',
    '🔎 Поиск по статьям',
    '🔄 Обновить данные',
    '🤳🏼 День за днём',
    'На главную',
]

AVAILABLE_AGES = [
    ('До родов', 0, 0),
    ('0-1 месяц', 1, 30),
    ('1-2 месяца', 31, 60),
    ('2-3 месяца', 61, 90),
    ('3-4 месяца', 91, 120),
    ('4-5 месяцев', 121, 150),
    ('5-6 месяцев', 151, 180),
]

AVAILABLE_AGES_initial = [
    ('До родов', 0, 0),
    ('Новорожденным', 0, 30),
    ('1-3 месяца', 31, 90),
    ('4-6 месяцев', 91, 180)
]


BANNED_USERS = [25125125125, 7707589700]
ADMINS = [1142511147]

# List of cities that are available for "Мой город" functionality
CITIES = []

# After what time daily article should be shown after registration
SEND_DAILY_ARTICLE_AFTER_REG = 5