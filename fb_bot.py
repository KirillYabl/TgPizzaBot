import enum
import logging
from typing import Any

import environs
from flask import Flask, request
from redis import Redis

import fb_api
import motlin_api

logger = logging.getLogger(__name__)
app = Flask(__name__)


class EventType(enum.Enum):
    MESSAGE = 'MESSAGE'
    POSTBACK = 'POSTBACK'


@app.route('/', methods=['GET'])
def verify():
    """
    При верификации вебхука у Facebook он отправит запрос на этот адрес. На него нужно ответить VERIFY_TOKEN.
    """
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == env.str("FB_VERIFY_TOKEN"):
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world", 200


def handle_start(sender_id: str, message_text: str, event_type: EventType) -> str:
    max_products_on_page = 10
    extra_elements = 2  # manage element and categories element
    max_buttons_for_element = 3
    if event_type == EventType.MESSAGE:
        category_id = env.str('MAIN_CATEGORY_ID', None)
    elif event_type == EventType.POSTBACK:
        if message_text.startswith('CATEGORY_ID:'):
            category_id = message_text.split('CATEGORY_ID:')[1]
    pizzas = motlin_api.get_products(access_keeper, category_id)[:max_products_on_page - extra_elements]
    categories = motlin_api.get_all_categories(access_keeper)
    elements = \
        [
            {
                'title': 'Меню',
                'subtitle': 'Добавьте пиццы в корзину и сделайте заказ',
                'image_url': env.str('PIZZA_LOGO_URL'),
                'buttons': [
                    {
                        'type': 'postback',
                        'title': 'Корзина',
                        'payload': 'CART'
                    },
                    {
                        'type': 'postback',
                        'title': 'Сделать заказ',
                        'payload': 'ORDER'
                    }
                ]
            }
        ] + [
            {
                'title': f'{pizza["name"]} ({pizza["meta"]["display_price"]["with_tax"]["formatted"]})',
                'subtitle': pizza['description'],
                'image_url': motlin_api.get_file_href_by_id(
                    access_keeper,
                    pizza['relationships']['main_image']['data']['id']
                ),
                'buttons': [{
                    'type': 'postback',
                    'title': 'Добавить в корзину',
                    'payload': f'ADD_TO_CART:{pizza["id"]}'
                }]
            }
            for pizza in pizzas
        ] + [
            {
                'title': 'Не нашли нужную пиццу?',
                'subtitle': 'Остальные пиццы можно посмотреть в одной из категорий',
                'image_url': env.str('PIZZA_CATEGORIES_URL'),
                'buttons': [
                               {
                                   'type': 'postback',
                                   'title': other_category['name'],
                                   'payload': f'CATEGORY_ID:{other_category["id"]}'
                               }
                               for other_category
                               in [category for category in categories if category['id'] != category_id]
                           ][:max_buttons_for_element - 1]
            }
        ]
    fb_api.send_carousel_buttons(env.str("FB_PAGE_ACCESS_TOKEN"), sender_id, elements)
    return 'MENU'


def construct_cart(sender_id: str) -> list[dict[str, Any]]:
    cart_items_info = motlin_api.get_cart_items_info(access_keeper, sender_id)
    total_price = cart_items_info['total_price']
    cart_elements = \
        [
            {
                'title': 'Корзина',
                'subtitle': f'Ваш заказ на сумму {total_price}',
                'image_url': env.str('CART_IMAGE_URL'),
                'buttons': [
                    {
                        'type': 'postback',
                        'title': 'Самовывоз',
                        'payload': 'PICKUP'
                    },
                    {
                        'type': 'postback',
                        'title': 'Доставка',
                        'payload': 'DELIVERY'
                    },
                    {
                        'type': 'postback',
                        'title': 'К меню',
                        'payload': 'MENU'
                    }
                ]
            }
        ] + [
            {
                'title': f'{item["name"]} ({item["quantity"]} шт.)',
                'subtitle': item['description'],
                'image_url': motlin_api.get_file_href_by_id(
                    access_keeper,
                    motlin_api.get_product_by_id(
                        access_keeper,
                        item["product_id"]
                    )['relationships']['main_image']['data']['id']
                ),
                'buttons': [
                    {
                        'type': 'postback',
                        'title': 'Добавить еще одну',
                        'payload': f'ADD_TO_CART:{item["product_id"]}'
                    },
                    {
                        'type': 'postback',
                        'title': 'Убрать из корзины',
                        'payload': f'REMOVE_FROM_CART:{item["cart_item_id"]}'
                    }
                ]
            }
            for item in cart_items_info['products']
        ]
    return cart_elements


def handle_menu(sender_id: str, message_text: str, event_type: EventType) -> str:
    if event_type == EventType.MESSAGE:
        return 'MENU'
    elif event_type == EventType.POSTBACK:
        if message_text.startswith('ADD_TO_CART:'):
            product_id = message_text.split('ADD_TO_CART:')[1]
            quantity = 1
            motlin_api.add_product_to_cart(access_keeper, product_id, quantity, sender_id)
            elements = construct_cart(sender_id)
        elif message_text == 'CART':
            elements = construct_cart(sender_id)
        elif message_text.startswith('REMOVE_FROM_CART:'):
            cart_item_id = message_text.split('REMOVE_FROM_CART:')[1]
            motlin_api.delete_cart_item(access_keeper, sender_id, cart_item_id)
            elements = construct_cart(sender_id)
        elif message_text == 'MENU':
            return 'START'
        fb_api.send_carousel_buttons(env.str("FB_PAGE_ACCESS_TOKEN"), sender_id, elements)
    return 'MENU'


def handle_users_reply(sender_id: str, message_text: str, event_type: EventType) -> None:
    states_functions = {
        'START': handle_start,
        'MENU': handle_menu,
    }
    recorded_state = DATABASE.get(f'facebookid_{sender_id}')
    if not recorded_state or recorded_state.decode("utf-8") not in states_functions.keys():
        user_state = "START"
    else:
        user_state = recorded_state.decode("utf-8")
    if message_text == "/start":
        user_state = "START"
    state_handler = states_functions[user_state]
    next_state = state_handler(sender_id, message_text, event_type)
    DATABASE.set(f'facebookid_{sender_id}', next_state)


@app.route('/', methods=['POST'])
def webhook():
    """
    Основной вебхук, на который будут приходить сообщения от Facebook.
    """
    logger.debug('webhook...')
    data = request.get_json()

    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"][
                        "id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    handle_users_reply(sender_id, message_text, EventType.MESSAGE)
                elif messaging_event.get("postback"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"][
                        "id"]  # the recipient's ID, which should be your page's facebook ID
                    payload = messaging_event["postback"]["payload"]  # the message's text
                    handle_users_reply(sender_id, payload, EventType.POSTBACK)
    return "ok", 200


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    env = environs.Env()
    env.read_env()
    access_keeper = motlin_api.Access(env.str('MOTLIN_CLIENT_ID'), env.str('MOTLIN_CLIENT_SECRET'))
    DATABASE = Redis(
        host=env.str('REDIS_DB_ADDRESS'),
        port=env.int('REDIS_DB_PORT'),
        password=env.str('REDIS_DB_PASSWORD')
    )
    app.run(debug=True)
