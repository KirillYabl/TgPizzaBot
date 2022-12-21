import copy
import json
import random
from typing import Dict, Any, List

import environs
import requests
from slugify import Slugify, CYRILLIC

from common_functions import raise_response_errors
import motlin_api


def get_json_response(url: str) -> Dict[Any, Any]:
    response = requests.get(url)
    raise_response_errors(response)
    return response.json()


def get_api_suitable_product(product: Dict[str, Any]) -> Dict[str, Any]:
    penny_to_rub_multiplier = 100
    slugify_ru = Slugify(pretranslate=CYRILLIC)
    suitable_for_api_product = {
        'data': {
            'type': 'product',
            'name': product['name'],
            'slug': slugify_ru(product['name']),
            'sku': str(random.randint(1, 2 ** 32)),
            'description': product.get('description', ''),
            'manage_stock': False,
            'price': [
                {
                    'amount': int(product['price']) * penny_to_rub_multiplier,
                    'currency': 'RUB',
                    'includes_tax': True,
                },
            ],
            'status': 'live',
            'commodity_type': 'physical',
        },
    }
    return suitable_for_api_product


def upload_menu(menu: List[Dict[str, Any]], access_keeper: motlin_api.Access):
    for product in menu:
        product_to_api = get_api_suitable_product(product)
        product_id = motlin_api.create_product(access_keeper, product_to_api)
        image_url = product.get('product_image', {}).get('url', '')
        if image_url:
            motlin_api.upload_image_to_product(access_keeper, product_id, image_url)


def create_address_flow(access_keeper, address_flow_data):
    address_flow = address_flow_data['address_flow']
    address_flow_id = motlin_api.create_flow(access_keeper, address_flow)

    field_template = address_flow_data['field_template']
    field_template['data']['relationships']['flow']['data']['id'] = address_flow_id

    address_fields = address_flow_data['address_fields']

    for address_field in address_fields:
        field_data = copy.deepcopy(field_template)
        for param_name, param_value in address_field.items():
            field_data['data'][param_name] = param_value
        motlin_api.create_field(access_keeper, field_data)


def get_api_suitable_address(address):
    suitable_for_api_address = {
        'data': {
            'type': 'entry',
            'pizzeria-addresses-address': address['address']['full'],
            'pizzeria-addresses-alias': address['alias'],
            'pizzeria-addresses-longitude': float(address['coordinates']['lon']),
            'pizzeria-addresses-latitude': float(address['coordinates']['lat']),
        }
    }
    return suitable_for_api_address


def upload_addresses(addresses, access_keeper, address_slug, test_telegram_chat_id=None):
    for address in addresses:
        address_to_api = get_api_suitable_address(address)
        if test_telegram_chat_id is not None:
            address_to_api['data']['pizzeria-addresses-deliveryman-telegram-chat-id'] = test_telegram_chat_id
        motlin_api.upload_entry_to_flow(access_keeper, address_to_api, address_slug)


def main():
    addresses_url = 'https://dvmn.org/media/filer_public/90/90/9090ecbf-249f-42c7-8635-a96985268b88/addresses.json'
    menu_url = 'https://dvmn.org/media/filer_public/a2/5a/a25a7cbd-541c-4caf-9bf9-70dcdf4a592e/menu.json'

    addresses = get_json_response(addresses_url)
    menu = get_json_response(menu_url)

    env = environs.Env()
    env.read_env()
    motlin_client_id = env.str('MOTLIN_CLIENT_ID')
    motlin_client_secret = env.str('MOTLIN_CLIENT_SECRET', None)
    test_telegram_chat_id = env.str('TEST_TELEGRAM_CHAT_ID', None)
    access_keeper = motlin_api.Access(motlin_client_id, motlin_client_secret)

    upload_menu(menu, access_keeper)

    with open('pizzeria_address_flow.json') as f:
        pizzeria_address_flow_data = json.load(f)
    create_address_flow(access_keeper, pizzeria_address_flow_data)
    pizzeria_address_slug = pizzeria_address_flow_data['address_flow']['data']['slug']
    upload_addresses(addresses, access_keeper, pizzeria_address_slug, test_telegram_chat_id)

    with open('customer_address_flow.json') as f:
        customer_address_flow_data = json.load(f)
    create_address_flow(access_keeper, customer_address_flow_data)


if __name__ == '__main__':
    main()
