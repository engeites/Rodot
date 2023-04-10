import logging

from aiogram.contrib.fsm_storage.redis import RedisStorage2
import redis

from app.database import user_crud

redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0, max_connections=5)

redis_client = redis.Redis(connection_pool=redis_pool)

storage = RedisStorage2(redis_client)


logger = logging.getLogger(__name__)

# load all admin users list
# list_of_admins = user_crud.get_all_admins()
ADMINS = [int(admin.username) for admin in user_crud.get_all_admins()]