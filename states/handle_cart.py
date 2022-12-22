import logging

from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

import motlin_api
from utils.cart_tg_utils import send_cart_info
from states.start import start

logger = logging.getLogger(__name__)


def handle_cart(update: Update, context: CallbackContext) -> str:
    """Cart menu."""
    bot = context.bot
    chat_id = update.effective_chat.id
    query = update.callback_query
    if query.data == 'to_menu':
        logger.debug('User chose return to menu')
        condition = start(update, context)
        return condition

    if query.data == 'payment':
        logger.debug('User chose payment')
        msg = 'Пожалуйста, пришлите ваш email'
        bot.send_message(text=msg, chat_id=chat_id)
        return 'WAITING_EMAIL'

    cart_item_id = query.data
    logger.debug(f'User deleting item from cart, cart_item_id: {cart_item_id}')
    motlin_api.delete_cart_item(context.bot_data['access_keeper'], chat_id, cart_item_id)

    condition = send_cart_info(context, update)
    return condition
