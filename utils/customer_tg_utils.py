from typing import Tuple
import logging

from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

import motlin_api

logger = logging.getLogger(__name__)


def get_customer_id(context: CallbackContext, update: Update, access_keeper: "motlin_api.Access") -> str:
    """Get customer_id from cache or from api."""
    customer_id = context.user_data.get('customer_id', None)
    if customer_id is not None:
        return customer_id

    customer_email = context.user_data.get('email', '')
    customer_name = update.effective_user.username
    customer_id = motlin_api.get_customer_id_by_name_and_email(access_keeper, customer_email, customer_name)
    return customer_id


def get_customer_id_or_waiting_email(context: CallbackContext, update: Update,
                                     access_keeper: "motlin_api.Access", chat_id: int) -> Tuple[str, str]:
    """Get customer_id or return WAITING_EMAIL condition if it was error while getting customer id."""
    try:
        logger.debug('getting customer id')
        customer_id = get_customer_id(context, update, access_keeper)
        logger.debug('got customer id')
        return customer_id, ''
    except motlin_api.WrongCustomersNumber:
        logger.warning('Can not find user by email')
        msg = 'Что-то пошло не так, пожалуйста, укажите снова свой emaıl'
        context.bot.send_message(text=msg, chat_id=chat_id)
        return '', 'WAITING_EMAIL'
