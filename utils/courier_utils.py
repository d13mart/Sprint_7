import requests
import random
import string
from typing import List, Optional, Dict, Any

BASE_URL = "https://qa-scooter.praktikum-services.ru/api/v1"


def _random_string(length: int) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(length))


def generate_courier_data() -> Dict[str, str]:
    """Генерирует уникальные данные для курьера (не регистрирует)."""
    return {
        "login": _random_string(10),
        "password": _random_string(10),
        "firstName": _random_string(10),
    }


def register_new_courier() -> Optional[List[str]]:
    """
    Генерирует уникального курьера, регистрирует его и возвращает
    [login, password, first_name]. Если регистрация не удалась - None.
    """
    payload = generate_courier_data()

    resp = requests.post(f"{BASE_URL}/courier", json=payload)
    if resp.status_code == 201:
        return [payload["login"], payload["password"], payload["firstName"]]
    return None


def delete_courier(courier_id: int) -> bool:
    """Удаляет курьера по его id. Возвращает True, если удаление успешно."""
    resp = requests.delete(f"{BASE_URL}/courier/{courier_id}")
    return resp.status_code == 200


def login_courier(login: str, password: str) -> Optional[Dict[str, Any]]:
    """Авторизация курьера. Возвращает JSON с id, если успешно."""
    resp = requests.post(f"{BASE_URL}/courier/login", json={"login": login, "password": password})
    if resp.status_code == 200:
        return resp.json()
    return None


def create_courier(login: str, password: str, first_name: str) -> Optional[Dict[str, Any]]:
    """Создаёт курьера. Возвращает JSON-ответ."""
    resp = requests.post(f"{BASE_URL}/courier", json={"login": login, "password": password, "firstName": first_name})
    return resp.json() if resp.status_code in (200, 201) else None