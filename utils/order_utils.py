import requests
from typing import Dict, List, Optional, Any

BASE_URL = "https://qa-scooter.praktikum-services.ru/api/v1"


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
    """
    Создаёт заказ. Возвращает JSON-ответ с track, если успешно, иначе None.
    """
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

    resp = requests.post(f"{BASE_URL}/orders", json=payload)
    if resp.status_code == 201:
        return resp.json()
    return None


def get_orders_list() -> Optional[List[Dict[str, Any]]]:
    """Возвращает список заказов."""
    resp = requests.get(f"{BASE_URL}/orders")
    if resp.status_code == 200:
        return resp.json().get("orders", [])
    return None


def get_order_by_track(track: int) -> Optional[Dict[str, Any]]:
    """Получает заказ по треку."""
    resp = requests.get(f"{BASE_URL}/orders/track", params={"t": track})
    if resp.status_code == 200:
        return resp.json().get("order")
    return None


def accept_order(order_id: int, courier_id: int) -> Optional[Dict[str, Any]]:
    """Принимает заказ курьером. courierId передается в query params."""
    resp = requests.put(f"{BASE_URL}/orders/accept/{order_id}", params={"courierId": courier_id})
    if resp.status_code == 200:
        return resp.json()
    return None


def cancel_order(order_id: int) -> Optional[Dict[str, Any]]:
    """Отменяет заказ (id в query params, как в задании)."""
    resp = requests.put(f"{BASE_URL}/orders/cancel", params={"track": order_id})
    if resp.status_code == 200:
        return resp.json()
    return None


def login_courier(login: str, password: str) -> Optional[Dict[str, Any]]:
    """Авторизация курьера. Возвращает JSON с id, если успешно."""
    resp = requests.post(f"{BASE_URL}/courier/login", json={"login": login, "password": password})
    if resp.status_code == 200:
        return resp.json()
    return None


def delete_courier(courier_id: int) -> bool:
    """Удаляет курьера по id."""
    resp = requests.delete(f"{BASE_URL}/courier/{courier_id}")
    return resp.status_code == 200


def create_courier(login: str, password: str, first_name: str) -> Optional[Dict[str, Any]]:
    """Создаёт курьера. Возвращает JSON-ответ."""
    resp = requests.post(f"{BASE_URL}/courier", json={"login": login, "password": password, "firstName": first_name})
    return resp.json() if resp.status_code in (200, 201) else None