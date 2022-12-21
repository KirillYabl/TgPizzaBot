import logging
from typing import Optional

from telegram import LabeledPrice
from telegram.ext.callbackcontext import CallbackContext
from telegram.update import Update

import motlin_api
from not_only_one_state_functions import get_customer_id_or_waiting_email
from singletons import access_keeper, config

logger = logging.getLogger(__name__)


def send_invoice(update: Update, context: CallbackContext, delivery_price: int = 0) -> None:
    bot = context.bot
    chat_id = update.effective_chat.id
    title = "Оплата"
    description = "Пожалуйста, оплатите вашу пиццу"
    # select a payload just for you to recognize its the donation from your bot
    payload = "Dvmn-Pizza-Bot-Payload"
    provider_token = config['bank_token']
    currency = "RUB"
    cart_items_info = motlin_api.get_cart_items_info(access_keeper, chat_id)
    price = cart_items_info['total_price_amount']
    price += delivery_price
    prices = [LabeledPrice("Test", price)]
    logger.debug('preliminaries for invoice sending ready')

    bot.sendInvoice(chat_id, title, description, payload,
                    provider_token, currency, prices)


def do_delivery(context, chat_id, deliveryman_chat_id, msg, lat, lon):
    context.bot.send_message(text=msg, chat_id=deliveryman_chat_id)
    context.bot.send_location(chat_id=deliveryman_chat_id, latitude=lat, longitude=lon)
    hour_seconds = 60 * 60
    context.job_queue.run_once(lambda context: callback_feedback(context, chat_id), when=hour_seconds,
                               context=context)


def do_pickup(context, msg, chat_id):
    context.bot.send_message(text=msg, chat_id=chat_id)
    hour_seconds = 60 * 60
    context.job_queue.run_once(lambda context: callback_feedback(context, chat_id), when=hour_seconds,
                               context=context)


def callback_feedback(context: CallbackContext, chat_id) -> None:
    msg = '''Приятного аппетита! *место для рекламы*
*сообщение что делать если пицца не пришла*'''
    context.bot.send_message(
        chat_id=chat_id,
        text=msg
    )


def waiting_delivery_type(update: Update, context: CallbackContext) -> Optional[str]:
    """Condition that wait type of delivery from user."""
    bot = context.bot
    chat_id = update.effective_chat.id
    query = update.callback_query
    logger.debug(f'query.data = {query.data}')

    customer_id, condition = get_customer_id_or_waiting_email(context, update, access_keeper, chat_id)
    if condition:
        return condition

    nearest_pizzeria = context.user_data.get('nearest_pizzeria', None)
    if nearest_pizzeria is None:
        logger.warning('No :nearest_pizzeria: in cache')
        msg = 'Что-то пошло не так, пожалуйста, укажите снова свой адрес'
        bot.send_message(text=msg, chat_id=chat_id)
        return 'WAITING_GEO'

    if query.data.startswith('delivery'):
        delivery_price = int(query.data.split(':')[-1])
        flow_slug = config['customer_addresses_flow_slug']
        customers = motlin_api.get_all_entries_of_flow(access_keeper, flow_slug)
        for customer in customers:
            if customer[config['customer_addresses_customer_id_slug']] == customer_id:
                lat = customer[config['customer_addresses_latitude_slug']]
                lon = customer[config['customer_addresses_longitude_slug']]
                break
        deliveryman_chat_id = nearest_pizzeria[config['pizzeria_addresses_deliveryman_telegram_chat_id']]
        msg = context.user_data['cart_msg']
        msg += f'\nСтоимость доставки: {delivery_price} руб.'
        delivery_price *= 100  # from rubles to cents
        context.user_data['succesful_callback'] = lambda: do_delivery(
            context, chat_id, deliveryman_chat_id, msg, lat, lon)

    else:
        delivery_price = 0
        nearest_pizzeria_address = nearest_pizzeria[config['pizzeria_addresses_address']]
        msg = f'Спасибо за ваш заказ, ваш заказ будет приготовлен в ближайшей к вам пиццерии по адресу: {nearest_pizzeria_address}'
        context.user_data['succesful_callback'] = lambda: do_pickup(context, msg, chat_id)

    send_invoice(update, context, delivery_price)
    return 'FAKE_CONDITION'
