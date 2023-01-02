import logging
import os
import json

import environs
import requests
from flask import Flask, request

import fb_api

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
    buttons = [
        {
            'type': 'postback',
            'title': 'new button',
            'payload': 'START',
        }
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
                    fb_api.send_buttons(env.str("FB_PAGE_ACCESS_TOKEN"), sender_id, buttons)
                    logger.debug('message sended')
    return "ok", 200


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    env = environs.Env()
    env.read_env()
    app.run(debug=True)
