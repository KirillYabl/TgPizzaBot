import logging

from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import motlin_api
from not_only_one_state_functions import send_cart_info
from singletons.access_keeper import access_keeper
from states.start import start

logger = logging.getLogger(__name__)


def handle_menu(update: Update, context: CallbackContext) -> str:
    """Menu with products."""
    bot = context.bot
    chat_id = update.effective_chat.id
    query = update.callback_query

    logger.debug(f'query.data = {query.data}')

    if query.data == 'cart':
        logger.debug('go to :send_cart_info: function')
        condition = send_cart_info(context, update)
        return condition
    elif query.data.startswith('page'):
        page_number = int(query.data.split('-')[-1])
        logger.debug(f'go to :start: function with page {page_number}')
        condition = start(update, context, page_number)
        return condition

    logger.debug('returning description of product')

    product_id = query.data
    product = motlin_api.get_product_by_id(access_keeper, product_id)
    image_id = product['relationships']['main_image']['data']['id']
    image_href = motlin_api.get_file_href_by_id(access_keeper, image_id)

    msg = f"""
    {product['name']}
    {product['meta']['display_price']['with_tax']['formatted']}
    {product['description']}
    """
    logger.debug('reply message was constructed')

    add_to_cart_buttons = []
    # If you need to add few variations (like 1, 3, 5 quantity) make a cycle and buttons will stand one-row
    callback_data = f'{product_id}\n1'
    add_to_cart_buttons.append(InlineKeyboardButton('Добавить в корзину', callback_data=callback_data))

    keyboard = [
        add_to_cart_buttons,
        [InlineKeyboardButton('Корзина', callback_data='cart')],
        [InlineKeyboardButton('Назад', callback_data='back_to_products')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    logger.debug('Keyboard was constructed')

    bot.send_photo(chat_id=chat_id, photo=image_href, caption=msg, reply_markup=reply_markup)
    bot.delete_message(chat_id=chat_id, message_id=query.message.message_id)
    return 'HANDLE_DESCRIPTION'
