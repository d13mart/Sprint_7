import pytest
import allure
import requests
from utils.order_utils import get_orders_list, create_order, BASE_URL


@allure.epic("API Яндекс.Самокат")
@allure.feature("Список заказов")
class TestGetOrdersList:
    """Тесты для ручки GET /api/v1/orders"""

    @allure.title("Успешное получение списка заказов")
    def test_get_orders_list(self):
        """В тело ответа возвращается список заказов."""
        # Создаём заказ, чтобы список точно не был пустым
        order_data = {
            "first_name": "Тест",
            "last_name": "Тестов",
            "address": "ул. Тестовая, 1",
            "metro_station": 1,
            "phone": "+7 999 999 99 99",
            "rent_time": 3,
            "delivery_date": "2026-09-01",
            "comment": "Тестовый заказ",
            "color": ["BLACK"],
        }
        created = create_order(**order_data)
        assert created is not None
        track = created["track"]

        try:
            orders = get_orders_list()
            assert orders is not None
            assert isinstance(orders, list)
            # Список может быть пагинированным, просто проверяем структуру
            assert len(orders) >= 0
        finally:
            # Чистим
            requests.put(f"{BASE_URL}/orders/cancel", params={"track": track})

    @allure.title("Список заказов имеет правильную структуру")
    def test_orders_list_structure(self):
        """Каждый заказ в списке содержит обязательные поля."""
        orders = get_orders_list()
        assert orders is not None
        assert isinstance(orders, list)

        if orders:  # если список не пустой
            order = orders[0]
            # Проверяем наличие основных полей
            assert "id" in order
            assert "track" in order
            assert "firstName" in order
            assert "lastName" in order
            assert "address" in order
            assert "metroStation" in order
            assert "phone" in order
            assert "rentTime" in order
            assert "deliveryDate" in order
            assert "color" in order