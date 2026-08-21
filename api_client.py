"""API клиент для Яндекс.Самокат с утилитами и retry-логикой."""
import requests
import random
import string
import time
from typing import Dict, List, Optional, Any, Callable
from functools import wraps

from config import BASE_URL


def _random_string(length: int) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def retry_on_network_error(max_attempts: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Декоратор для ретраев при сетевых ошибках."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout, requests.exceptions.Timeout) as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
            raise last_exception
        return wrapper
    return decorator


class SamokatAPI:
    """Клиент для работы с API Яндекс.Самокат."""

    @staticmethod
    def generate_courier_data() -> Dict[str, str]:
        """Генерирует уникальные данные для курьера (не регистрирует)."""
        return {
            "login": _random_string(10),
            "password": _random_string(10),
            "firstName": _random_string(10),
        }

    @staticmethod
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def create_courier(login: str, password: str, first_name: str) -> Optional[Dict[str, Any]]:
        """Создаёт курьера. Возвращает JSON-ответ."""
        resp = requests.post(
            f"{BASE_URL}/courier",
            json={"login": login, "password": password, "firstName": first_name},
            timeout=(10, 30)
        )
        return resp.json() if resp.status_code in (200, 201) else None

    @staticmethod
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def login_courier(login: str, password: str) -> Optional[Dict[str, Any]]:
        """Авторизация курьера. Возвращает JSON с id, если успешно."""
        resp = requests.post(
            f"{BASE_URL}/courier/login",
            json={"login": login, "password": password},
            timeout=(10, 30)
        )
        if resp.status_code == 200:
            return resp.json()
        return None

    @staticmethod
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def delete_courier(courier_id: int) -> bool:
        """Удаляет курьера по его id."""
        resp = requests.delete(
            f"{BASE_URL}/courier/{courier_id}",
            timeout=(10, 30)
        )
        return resp.status_code == 200

    @staticmethod
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def create_order(
        first_name: str,
        last_name: str,
        address: str,
        metro_station: int,
        phone: str,
        rent_time: int,
        delivery_date: str,
        comment: str,
        color: List[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Создаёт заказ. Возвращает JSON-ответ с track, если успешно."""
        payload = {
            "firstName": first_name,
            "lastName": last_name,
            "address": address,
            "metroStation": metro_station,
            "phone": phone,
            "rentTime": rent_time,
            "deliveryDate": delivery_date,
            "comment": comment,
        }
        if color:
            payload["color"] = color

        resp = requests.post(f"{BASE_URL}/orders", json=payload, timeout=(10, 30))
        if resp.status_code == 201:
            return resp.json()
        return None

    @staticmethod
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def get_orders_list() -> Optional[List[Dict[str, Any]]]:
        """Возвращает список заказов."""
        resp = requests.get(f"{BASE_URL}/orders", timeout=(10, 30))
        if resp.status_code == 200:
            return resp.json().get("orders", [])
        return None

    @staticmethod
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def get_order_by_track(track: int) -> Optional[Dict[str, Any]]:
        """Получает заказ по треку (один запрос, ретраи для сети)."""
        resp = requests.get(f"{BASE_URL}/orders/track", params={"t": track}, timeout=(10, 30))
        if resp.status_code == 200:
            return resp.json().get("order")
        return None

    @staticmethod
    def get_order_by_track_with_retry(track: int, max_attempts: int = 5, delay: float = 0.5) -> Optional[Dict[str, Any]]:
        """Получает заказ по треку с ретраями на случай, если заказ ещё не готов после создания."""
        for _ in range(max_attempts):
            resp = requests.get(f"{BASE_URL}/orders/track", params={"t": track}, timeout=(10, 30))
            if resp.status_code == 200:
                order = resp.json().get("order")
                if order is not None:
                    return order
            time.sleep(delay)
        return None

    @staticmethod
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def accept_order(order_id: int, courier_id: int) -> Optional[Dict[str, Any]]:
        """Принимает заказ курьером. courierId передается в query params."""
        resp = requests.put(
            f"{BASE_URL}/orders/accept/{order_id}",
            params={"courierId": courier_id},
            timeout=(10, 30)
        )
        if resp.status_code == 200:
            return resp.json()
        return None

    @staticmethod
    @retry_on_network_error(max_attempts=3, delay=1.0)
    def cancel_order(track: int) -> Optional[Dict[str, Any]]:
        """Отменяет заказ (track в query params)."""
        resp = requests.put(
            f"{BASE_URL}/orders/cancel",
            params={"track": track},
            timeout=(10, 30)
        )
        if resp.status_code == 200:
            return resp.json()
        return None


# Для обратной совместимости экспортируем функции
api = SamokatAPI()

generate_courier_data = api.generate_courier_data
create_courier = api.create_courier
login_courier = api.login_courier
delete_courier = api.delete_courier
create_order = api.create_order
get_orders_list = api.get_orders_list
get_order_by_track = api.get_order_by_track
get_order_by_track_with_retry = api.get_order_by_track_with_retry
accept_order = api.accept_order
cancel_order = api.cancel_order