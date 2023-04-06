import logging

from aiogram.contrib.fsm_storage.redis import RedisStorage2
import redis

redis_pool = redis.ConnectionPool(host='localhost', port=6379, db=0, max_connections=5)

redis_client = redis.Redis(connection_pool=redis_pool)

storage = RedisStorage2(redis_client)


logger = logging.getLogger(__name__)