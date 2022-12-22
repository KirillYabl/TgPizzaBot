from typing import Dict, Any, Tuple, Optional
import logging

import requests

logger = logging.getLogger(__name__)


def fetch_coordinates(apikey: str, address: str) -> Optional[Tuple[float, float]]:
    # https://dvmn.org/encyclopedia/api-docs/yandex-geocoder-api/
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lon, lat


def get_address_entry_lat_lon(entry: Dict[str, Any]) -> Tuple[float, float]:
    return entry['pizzeria-addresses-latitude'], entry['pizzeria-addresses-longitude']


def get_delivery_price_by_distance(distance: float) -> Tuple[bool, int, str]:
    """Compute is order deliverable, price and human message."""
    if distance <= 0.5:
        return True, 0, 'Доставка бесплатно! Или можете оформить самовывоз.'
    elif distance <= 5:
        return True, 100, 'Доставка будет стоить 100 руб. Или можете оформить самовывоз.'
    elif distance <= 20:
        return True, 300, 'Доставка будет стоить 300 руб. Или можете оформить самовывоз.'
    else:
        return False, 0, 'Доставка не производится, вы можете забрать заказ самостотельно.'
