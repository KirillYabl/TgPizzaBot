"""The module with functions which useful for more then one state and bot itself"""

import logging
from typing import Optional

from telegram.ext import Updater, Filters, PreCheckoutQueryHandler
from telegram.ext import CommandHandler, CallbackQueryHandler, MessageHandler
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update
import redis

from not_only_one_state_functions import get_config
from states.handle_cart import handle_cart
from states.handle_description import handle_description
from states.handle_menu import handle_menu
from states.start import start
from states.waiting_delivery_type import waiting_delivery_type
from states.waiting_email import waiting_email
from states.waiting_geo import waiting_geo

logger = logging.getLogger(__name__)


def get_database_connection() -> redis.Redis:
    """Returns a connection to Redis DB or creates a new one if it does not already exist."""
    global _database
    try:
        return _database
    except NameError:
        pass
    config = get_config()
    _database = redis.Redis(host=config['redis_db_address'],
                            port=config['redis_db_port'],
                            password=config['redis_db_password'])
    logger.debug('connection with Redis DB was established')
    return _database


def successful_payment_callback(update: Update, context: CallbackContext) -> str:
    # do something after successful receive of payment?
    update.message.reply_text("Thank you for your payment!")
    context.user_data['succesful_callback']()
    del context.user_data['succesful_callback']

    condition = start(update, context)
    return condition


def precheckout_callback(update: Update, context: CallbackContext) -> Optional[str]:
    query = update.pre_checkout_query
    if 'succesful_callback' not in context.user_data or not context.user_data['succesful_callback']:
        logger.warning('Can not find succesful_callback')
        msg = 'Что-то пошло не так, пожалуйста, попробуйте снова сделать заказ'
        context.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=False, error_message=msg)
        condition = start(update, context)
        return condition
    context.bot.answer_pre_checkout_query(pre_checkout_query_id=query.id, ok=True)


def handle_users_reply(update: Update, context: CallbackContext) -> None:
    """Bot's state machine."""
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = update.message.chat_id
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = update.callback_query.message.chat_id
    else:
        return

    if user_reply == '/start':
        user_state = 'START'
        db.set(chat_id, user_state)
    else:
        user_state = db.get(chat_id).decode("utf-8")

    logger.debug(f'User state: {user_state}')

    states_functions = {
        'START': start,
        'HANDLE_MENU': handle_menu,
        'HANDLE_DESCRIPTION': handle_description,
        'HANDLE_CART': handle_cart,
        'WAITING_EMAIL': waiting_email,
        'WAITING_GEO': waiting_geo,
        'WAITING_DELIVERY_TYPE': waiting_delivery_type
    }
    state_handler = states_functions[user_state]
    next_state = state_handler(update, context)
    db.set(chat_id, next_state)


def error(update: Update, context: CallbackContext) -> None:
    """Log Errors caused by Updates."""
    logger.warning(f'Update "{update}" caused error "{context.error}"')


def main():
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s  %(message)s', level=logging.DEBUG)

    config = get_config()
    # Create the Updater and pass it your bot's token.
    request_kwargs = None
    if config['proxy']:
        request_kwargs = {'proxy_url': config['proxy']}
        logger.debug(f'Using proxy - {config["proxy"]}')
    updater = Updater(token=config['tg_bot_token'], use_context=True, request_kwargs=request_kwargs)
    logger.debug('Connection with TG was established')

    updater.dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    updater.dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    updater.dispatcher.add_handler(MessageHandler(Filters.successful_payment, successful_payment_callback))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # need to job queue work
    # https://stackoverflow.com/questions/70673175/runtimeerror-cannot-schedule-new-futures-after-interpreter-shutdown/70722653#70722653
    updater.idle()


if __name__ == '__main__':
    main()
