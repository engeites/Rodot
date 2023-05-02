import logging

from app.database import user_crud

logger = logging.getLogger(__name__)

# load all admin users list
# list_of_admins = user_crud.get_all_admins()
ADMINS = [int(admin.username) for admin in user_crud.get_all_admins()]