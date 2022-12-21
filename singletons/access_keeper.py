"""Pythonic way of singleton, module import only once"""

import environs
import logging

from motlin_api import Access

logger = logging.getLogger(__name__)

env = environs.Env()
env.read_env()

client_id = env.str("MOTLIN_CLIENT_ID")
client_secret = env.str("MOTLIN_CLIENT_SECRET", None)

access_keeper = Access(client_id, client_secret)
logger.debug('access_keeper was got')
