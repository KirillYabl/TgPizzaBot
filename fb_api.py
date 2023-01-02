import json
import logging

import requests

logger = logging.getLogger(__name__)


def send_message(token: str, recipient_id: str, message_text: str) -> None:
    """Send message"""
    logger.debug('sending message...')
    params = {"access_token": token}
    headers = {"Content-Type": "application/json"}
    request_content = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    response = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers,
                             data=request_content)
    response.raise_for_status()
    logger.debug('message sent')


def send_buttons(token: str, recipient_id: str, buttons: list[dict[str, str]]) -> None:
    """Send buttons"""
    logger.debug('sending buttons...')
    params = {"access_token": token}
    headers = {'Content-Type': 'application/json'}

    request_content = json.dumps({
        'recipient': {
            'id': recipient_id,
        },
        'message': {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'button',
                    'text': 'Try the postback button!',
                    'buttons': buttons,
                },
            },
        },
    })

    response = requests.post('https://graph.facebook.com/v2.6/me/messages',
                             headers=headers, data=request_content, params=params)
    response.raise_for_status()
    logger.debug('buttons sent')
