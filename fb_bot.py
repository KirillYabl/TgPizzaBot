import logging

import environs
from flask import Flask, request
from redis import Redis

import fb_api
import motlin_api

logger = logging.getLogger(__name__)
app = Flask(__name__)


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


def handle_start(sender_id, message_text):
    max_products_on_page = 10
    extra_elements = 2  # manage element and categories element
    max_buttons_for_element = 3
    main_category_id = env.str('MAIN_CATEGORY_ID', None)
    pizzas = motlin_api.get_products(access_keeper, main_category_id)[:max_products_on_page - extra_elements]
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
                               in [category for category in categories if category['id'] != main_category_id]
                           ][:max_buttons_for_element - 1]
            }
        ]
    fb_api.send_carousel_buttons(env.str("FB_PAGE_ACCESS_TOKEN"), sender_id, elements)
    return "START"


def handle_users_reply(sender_id, message_text):
    states_functions = {
        'START': handle_start,
    }
    recorded_state = DATABASE.get(f'facebookid_{sender_id}')
    if not recorded_state or recorded_state.decode("utf-8") not in states_functions.keys():
        user_state = "START"
    else:
        user_state = recorded_state.decode("utf-8")
    if message_text == "/start":
        user_state = "START"
    state_handler = states_functions[user_state]
    next_state = state_handler(sender_id, message_text)
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
                    handle_users_reply(sender_id, message_text)
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
