import logging

from app.database import user_crud




file_handler = logging.FileHandler('rodot.log')
file_handler.setLevel(logging.INFO)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[
        file_handler,
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# load all admin users list
# list_of_admins = user_crud.get_all_admins()
ADMINS = [int(admin.username) for admin in user_crud.get_all_admins()]