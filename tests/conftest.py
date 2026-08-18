import pytest
import requests
from utils.courier_utils import register_new_courier, delete_courier


@pytest.fixture(scope="session")
def api_client():
    """Клиент, которым пользуются все тесты."""
    return requests.Session()


@pytest.fixture(scope="function")
def new_courier(api_client):
    """
    Создаёт нового курьера перед тестом и удаляет его после.
    Возвращает словарь с полями login, password, first_name, id.
    """
    data = register_new_courier()
    if not data:
        pytest.fail("Не удалось зарегистрировать курьера")

    login, password, first_name = data
    resp = api_client.post(
        "https://qa-scooter.praktikum-services.ru/api/v1/courier",
        json={"login": login, "password": password, "firstName": first_name},
    )
    assert resp.status_code == 201
    courier_id = resp.json()["id"]

    yield {"login": login, "password": password, "first_name": first_name, "id": courier_id}

    # Тест завершён – чистим
    delete_courier(courier_id)