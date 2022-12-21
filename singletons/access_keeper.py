"""Pythonic way of singleton, module import only once"""

import logging

from motlin_api import Access
from .config import config

logger = logging.getLogger(__name__)

# Access singleton
access_keeper = Access(config['motlin_client_id'], config['motlin_client_secret'])
logger.debug('access_keeper was got')
