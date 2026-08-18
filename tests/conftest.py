"""Конфигурация pytest и фикстуры для API тестов."""
import pytest
import allure
from api_client import api, generate_courier_data


# ==================== Фикстуры для курьера ====================

@pytest.fixture(scope="function")
def courier_data():
    """Генерирует уникальные данные курьера (не регистрирует)."""
    return generate_courier_data()


@pytest.fixture(scope="function")
def created_courier(courier_data):
    """
    Создаёт курьера перед тестом и удаляет после.
    Возвращает словарь с login, password, first_name, courier_id.
    """
    data = courier_data
    # Создаём курьера
    create_resp = api.create_courier(data["login"], data["password"], data["firstName"])
    assert create_resp is not None, "Не удалось создать курьера"
    
    # Логинимся чтобы получить id
    login_resp = api.login_courier(data["login"], data["password"])
    assert login_resp is not None, "Не удалось авторизоваться"
    courier_id = login_resp["id"]
    
    yield {
        "login": data["login"],
        "password": data["password"],
        "first_name": data["firstName"],
        "courier_id": courier_id
    }
    
    # Чистим после теста
    api.delete_courier(courier_id)


@pytest.fixture(scope="function")
def logged_in_courier(created_courier):
    """Возвращает данные залогиненного курьера с id."""
    return created_courier


# ==================== Фикстуры для заказа ====================

@pytest.fixture(scope="function")
def order_data():
    """Базовые валидные данные для заказа."""
    return {
        "first_name": "Тест",
        "last_name": "Тестов",
        "address": "ул. Тестовая, 1",
        "metro_station": 1,
        "phone": "+7 999 999 99 99",
        "rent_time": 3,
        "delivery_date": "2026-09-01",
        "comment": "Тестовый заказ",
    }


@pytest.fixture(scope="function")
def created_order(order_data):
    """
    Создаёт заказ перед тестом и отменяет после.
    Возвращает dict с track и order_id.
    """
    created = api.create_order(**order_data, color=["BLACK"])
    assert created is not None, "Не удалось создать заказ"
    track = created["track"]
    
    # Получаем order_id (может потребоваться небольшая задержка)
    import time
    order = None
    for _ in range(5):
        order = api.get_order_by_track(track)
        if order is not None:
            break
        time.sleep(0.5)
    assert order is not None, f"Заказ с track={track} не найден после создания"
    order_id = order["id"]
    
    yield {
        "track": track,
        "order_id": order_id
    }
    
    # Чистим после теста
    api.cancel_order(track)


# ==================== Allure конфигурация ====================

def pytest_configure(config):
    """Настройка маркеров для pytest."""
    config.addinivalue_line("markers", "smoke: mark test as smoke test")
    config.addinivalue_line("markers", "regression: mark test as regression test")
    config.addinivalue_line("markers", "api: mark test as API test")


@pytest.fixture(autouse=True)
def allure_env():
    """Добавляет информацию об окружении в Allure отчёт."""
    import os
    # allure.environment is not available in allure-pytest
    # Environment info can be added via allure.environment in pytest_configure or via allure-results/environment.properties
    pass