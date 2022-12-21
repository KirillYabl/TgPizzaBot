import logging
import time

from geopy import distance
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import motlin_api
from not_only_one_state_functions import get_address_entry_lat_lon
from not_only_one_state_functions import get_customer_id_or_waiting_email
from not_only_one_state_functions import get_delivery_price
from not_only_one_state_functions import fetch_coordinates
from singletons.access_keeper import access_keeper
from singletons.config import config

logger = logging.getLogger(__name__)


def waiting_geo(update: Update, context: CallbackContext) -> str:
    """Condition that wait geo from user."""
    logger.debug('processing user geo...')
    bot = context.bot
    chat_id = update.effective_chat.id

    if update.message and update.message.location:
        logger.debug('user send location by telegram')
        current_pos = (update.message.location.longitude, update.message.location.latitude)
    elif update.message:
        logger.debug('user send location by text')
        apikey = config['yandex_geo_apikey']
        current_pos = fetch_coordinates(apikey, update.message.text)
    else:
        logger.debug('user did not send any message')
        current_pos = None

    if current_pos is None:
        logger.debug('User entered invalid geo')
        msg = 'Вы указали нусуществующий адрес, пожалуйста пришлите снова'
        bot.send_message(text=msg, chat_id=update.message.chat_id)
        return 'WAITING_GEO'

    user_lon, user_lat = current_pos
    now = int(time.time())
    seconds_in_day = 86400

    # pizzeria_addresses and last update will cache in config
    pizza_addresses = config.get('pizzeria_addresses', [])
    pizza_addresses_last_update = config.get('pizzeria_addresses_last_update', 0)
    need_update_by_time = now - pizza_addresses_last_update > seconds_in_day

    if not pizza_addresses or need_update_by_time:
        pizzeria_addresses_flow_slug = config['pizzeria_addresses_flow_slug']
        pizza_addresses = motlin_api.get_all_entries_of_flow(access_keeper, pizzeria_addresses_flow_slug)
        config['pizzeria_addresses'] = pizza_addresses
        config['pizzeria_addresses_last_update'] = now

    nearest_pizzeria = min(
        pizza_addresses,
        key=lambda entry: distance.distance(
            get_address_entry_lat_lon(entry),
            (user_lat, user_lon)
        )
    )
    context.user_data['nearest_pizzeria'] = nearest_pizzeria
    nearest_pizzeria_distance_km = distance.distance(
        get_address_entry_lat_lon(nearest_pizzeria),
        (user_lat, user_lon)
    ).km

    customer_id, condition = get_customer_id_or_waiting_email(context, update, access_keeper, chat_id)
    if condition:
        return condition

    # write to cms customer location
    customer_addresses_flow_slug = config['customer_addresses_flow_slug']
    entry = {
        'data': {
            'type': 'entry',
            config['customer_addresses_customer_id_slug']: customer_id,
            config['customer_addresses_longitude_slug']: float(user_lon),
            config['customer_addresses_latitude_slug']: float(user_lat),
        }
    }
    motlin_api.upload_entry_to_flow(access_keeper, entry, customer_addresses_flow_slug)

    # add delivery type buttons
    is_deliverable, delivery_price, msg = get_delivery_price(nearest_pizzeria_distance_km)
    delivery_btn = InlineKeyboardButton('Доставка', callback_data=f'delivery:{delivery_price}')
    pickup_btn = InlineKeyboardButton('Самовывоз', callback_data='pickup')
    if is_deliverable:
        keyboard = [[delivery_btn], [pickup_btn]]
    else:
        keyboard = [[pickup_btn]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    bot.send_message(text=msg, chat_id=chat_id, reply_markup=reply_markup)

    return 'WAITING_DELIVERY_TYPE'
