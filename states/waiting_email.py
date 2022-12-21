import logging

from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

import motlin_api
from common_functions import get_motlin_access_keeper

logger = logging.getLogger(__name__)


def waiting_email(update: Update, context: CallbackContext) -> str:
    """Condition that wait email from user."""
    logger.debug('processing user email..')
    bot = context.bot
    # if user send button for example instead of text email, that means invalid email
    user_email = ''
    if update.message:
        user_email = update.message.text
    access_keeper = get_motlin_access_keeper()

    customer_or_status_code = motlin_api.create_customer(access_keeper=access_keeper,
                                                         name=update.message.chat.username,
                                                         email=user_email)

    if customer_or_status_code == 422:
        # invalid email
        logger.debug('User entered invalid data')
        msg = 'Вы ввели неправильный email, пожалуйста пришлите снова, пример: example@gmail.com'
        bot.send_message(text=msg, chat_id=update.message.chat_id)
        return 'WAITING_EMAIL'

    if customer_or_status_code != 409:
        # email has not added to CMS yet
        logger.debug('New customer was created')
        user_email = customer_or_status_code['data']['email']
        context.user_data['customer_id'] = customer_or_status_code['data']['id']

    msg = f'Вы прислали мне эту почту: {user_email}.\nПожалуйста, пришлите адрес доставки.'
    context.user_data['email'] = user_email
    bot.send_message(text=msg, chat_id=update.message.chat_id)
    logger.debug('user email was processed')

    return 'WAITING_GEO'
