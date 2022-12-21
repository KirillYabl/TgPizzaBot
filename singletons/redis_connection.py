import logging

import redis

from .config import config

logger = logging.getLogger(__name__)

redis_connection = redis.Redis(
    host=config['redis_db_address'],
    port=config['redis_db_port'],
    password=config['redis_db_password']
)
logger.debug('connection with Redis DB was established')
