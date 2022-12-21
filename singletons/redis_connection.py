"""Pythonic way of singleton, module import only once"""

import environs
import logging

import redis

env = environs.Env()
env.read_env()

logger = logging.getLogger(__name__)

redis_db_password = env.str("REDIS_DB_PASSWORD")
redis_db_address = env.str("REDIS_DB_ADDRESS")
redis_db_port = env.int("REDIS_DB_PORT")

redis_connection = redis.Redis(
    host=redis_db_address,
    port=redis_db_port,
    password=redis_db_password
)
logger.debug('connection with Redis DB was established')
