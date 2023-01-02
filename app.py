import logging

import environs
from flask import Flask, request

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


@app.route('/', methods=['POST'])
def webhook():
    """
    Основной вебхук, на который будут приходить сообщения от Facebook.
    """
    logger.debug('webhook...')
    data = request.get_json()
    pizzas = motlin_api.get_all_products(access_keeper)[:6]
    elements = [
        {
            'title': f'{pizza["name"]} (product["meta"]["display_price"]["with_tax"]["formatted"])',
            'subtitle': pizza['description'],
            'buttons': {
                'type': 'postback',
                'title': 'Добавить в корзину',
                'payload': f'ADD_TO_CART:{pizza["id"]}'
            }
        }
        for pizza in pizzas
    ]
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                if messaging_event.get("message"):  # someone sent us a message
                    sender_id = messaging_event["sender"]["id"]  # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"][
                        "id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text
                    logger.debug(f'sending message(sender={sender_id};recipient={recipient_id};text={message_text})...')
                    fb_api.send_carousel_buttons(env.str("FB_PAGE_ACCESS_TOKEN"), sender_id, elements)
                    logger.debug('message sended')
    return "ok", 200


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    env = environs.Env()
    env.read_env()
    access_keeper = motlin_api.Access(env.str('MOTLIN_CLIENT_ID'), env.str('MOTLIN_CLIENT_SECRET'))
    app.run(debug=True)
