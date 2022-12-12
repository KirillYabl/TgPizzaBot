import logging

import motlin_api
import telegram

from common_functions import get_motlin_access_keeper, get_chat_id, send_cart_info
from states.start import start

logger = logging.getLogger(__name__)

# for typing
ContextType = telegram.ext.callbackcontext.CallbackContext
UpdateType = telegram.update.Update


def handle_cart(update: UpdateType, context: ContextType) -> str:
    """Cart menu."""
    bot = context.bot
    chat_id = get_chat_id(update)
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

    access_keeper = get_motlin_access_keeper()
    cart_item_id = query.data
    logger.debug(f'User deleting item from cart, cart_item_id: {cart_item_id}')
    motlin_api.delete_cart_item(access_keeper, chat_id, cart_item_id)

    condition = send_cart_info(context, update)
    return condition
