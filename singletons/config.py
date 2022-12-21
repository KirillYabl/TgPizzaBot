"""Pythonic way of singleton, module import only once"""

import environs
import logging

logger = logging.getLogger(__name__)

env = environs.Env()
env.read_env()

# config singleton
config = {
    'tg_bot_token': env.str('TG_BOT_TOKEN'), 'proxy': env.str('PROXY', None),
    'motlin_client_id': env.str("MOTLIN_CLIENT_ID"), 'motlin_client_secret': env.str("MOTLIN_CLIENT_SECRET"),
    'redis_db_password': env.str("REDIS_DB_PASSWORD"), 'redis_db_address': env.str("REDIS_DB_ADDRESS"),
    'redis_db_port': env.int("REDIS_DB_PORT"), 'products_on_page': env.int("PRODUCTS_ON_PAGE", 8),
    'yandex_geo_apikey': env.str("YANDEX_GEO_APIKEY"),
    'pizzeria_addresses_flow_slug': env.str("PIZZERIA_ADDRESSES_FLOW_SLUG", "pizzeria-addresses"),
    'customer_addresses_flow_slug': env.str("CUSTOMER_ADDRESSES_FLOW_SLUG", "customer-addresses"),
    'customer_addresses_customer_id_slug': env.str("CUSTOMER_ADDRESSES_CUSTOMER_ID_SLUG",
                                                   "customer-addresses-customer-id"),
    'customer_addresses_longitude_slug': env.str("CUSTOMER_ADDRESSES_LONGITUDE_SLUG", "customer-addresses-longitude"),
    'customer_addresses_latitude_slug': env.str("CUSTOMER_ADDRESSES_LATITUDE_SLUG", "customer-addresses-latitude"),
    'pizzeria_addresses_deliveryman_telegram_chat_id': env.str(
        "PIZZERIA_ADDRESSES_DELIVERYMAN_TELEGRAM_CHAT_ID",
        "pizzeria-addresses-deliveryman-telegram-chat-id"),
    'pizzeria_addresses_address': env.str("PIZZERIA_ADDRESSES_ADDRESS", "pizzeria-addresses-address"),
    'bank_token': env.str("BANK_TOKEN")
}
logger.debug('.env was read, config was constructed')
