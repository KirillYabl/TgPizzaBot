"""The module with functions which useful for more then one state and bot itself"""

from typing import Dict, Any, Tuple, Optional
import logging

import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

import motlin_api
from singletons.access_keeper import access_keeper

logger = logging.getLogger(__name__)


def fetch_coordinates(apikey: str, address: str) -> Optional[Tuple[float, float]]:
    # https://dvmn.org/encyclopedia/api-docs/yandex-geocoder-api/
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_address_entry_lat_lon(entry: Dict[str, Any]) -> Tuple[float, float]:
    return entry['pizzeria-addresses-latitude'], entry['pizzeria-addresses-longitude']


def get_delivery_price(distance: float) -> Tuple[bool, int, str]:
    """Compute is order deliverable, price and human message."""
    if distance <= 0.5:
        return True, 0, 'Доставка бесплатно! Или можете оформить самовывоз.'
    elif distance <= 5:
        return True, 100, 'Доставка будет стоить 100 руб. Или можете оформить самовывоз.'
    elif distance <= 20:
        return True, 300, 'Доставка будет стоить 300 руб. Или можете оформить самовывоз.'
    else:
        return False, 0, 'Доставка не производится, вы можете забрать заказ самостотельно.'


def send_cart_info(context: CallbackContext, update: Update) -> str:
    """Send message with cart info (name, description, price per unit, quantity, total_price)."""
    bot = context.bot
    chat_id = update.effective_chat.id
    cart_items_info = motlin_api.get_cart_items_info(access_keeper, chat_id)
    total_price = cart_items_info['total_price']
    product_messages = []
    keyboard = []
    for item in cart_items_info['products']:
        item_msg = f'{item["name"]}\n{item["description"]}\n{item["price_per_unit"]} шт.\n'
        item_msg += f'{item["quantity"]} шт. в корзине за {item["total_price"]}'
        product_messages.append(item_msg)

        keyboard.append([InlineKeyboardButton(f'Убрать из корзины {item["name"]}', callback_data=item['cart_item_id'])])

        logger.debug(f'item {item["cart_item_id"]} was processed, btn added')

    keyboard.append([InlineKeyboardButton('В меню', callback_data='to_menu')])
    keyboard.append([InlineKeyboardButton('Оплата', callback_data='payment')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    logger.debug(f'keyboard was constructed')

    msg = '\n\n'.join(product_messages) + f'\n\nОбщая цена: {total_price}'
    context.user_data['cart_msg'] = msg

    bot.send_message(text=msg, chat_id=chat_id, reply_markup=reply_markup)

    return 'HANDLE_CART'


def get_customer_id(context: CallbackContext, update: Update, access_keeper: "motlin_api.Access") -> str:
    """Get customer_id from cache or from api."""
    customer_id = context.user_data.get('customer_id', None)
    if customer_id is not None:
        return customer_id

    customer_email = context.user_data.get('email', '')
    customer_name = update.effective_user.username
    customer_id = motlin_api.get_customer_id_by_name_and_email(access_keeper, customer_email, customer_name)
    return customer_id


def get_customer_id_or_waiting_email(context: CallbackContext, update: Update,
                                     access_keeper: "motlin_api.Access", chat_id: int) -> Tuple[str, str]:
    """Get customer_id or return WAITING_EMAIL condition if it was error while getting customer id."""
    try:
        logger.debug('getting customer id')
        customer_id = get_customer_id(context, update, access_keeper)
        logger.debug('got customer id')
        return customer_id, ''
    except motlin_api.WrongCustomersNumber:
        logger.warning('Can not find user by email')
        msg = 'Что-то пошло не так, пожалуйста, укажите снова свой emaıl'
        context.bot.send_message(text=msg, chat_id=chat_id)
        return '', 'WAITING_EMAIL'
