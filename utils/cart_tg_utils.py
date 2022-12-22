import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

import motlin_api

logger = logging.getLogger(__name__)


def send_cart_info(context: CallbackContext, update: Update) -> str:
    """Send message with cart info (name, description, price per unit, quantity, total_price)."""
    bot = context.bot
    chat_id = update.effective_chat.id
    cart_items_info = motlin_api.get_cart_items_info(context.bot_data['access_keeper'], chat_id)
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
    logger.debug('keyboard was constructed')

    msg = '\n\n'.join(product_messages) + f'\n\nОбщая цена: {total_price}'
    context.user_data['cart_msg'] = msg

    bot.send_message(text=msg, chat_id=chat_id, reply_markup=reply_markup)

    return 'HANDLE_CART'
