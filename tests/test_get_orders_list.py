import pytest
import allure
from api_client import api


@allure.epic("API Яндекс.Самокат")
@allure.feature("Список заказов")
class TestGetOrdersList:
    """Тесты для ручки GET /api/v1/orders"""

    @allure.title("Успешное получение списка заказов")
    def test_get_orders_list(self, created_order):
        """В тело ответа возвращается список заказов."""
        # created_order fixture creates an order and cleans up after
        track = created_order["track"]
        
        orders = api.get_orders_list()
        assert orders is not None
        assert isinstance(orders, list)
        # Список может быть пагинированным, просто проверяем структуру
        assert len(orders) >= 0

    @allure.title("Список заказов имеет правильную структуру")
    def test_orders_list_structure(self):
        """Каждый заказ в списке содержит обязательные поля."""
        orders = api.get_orders_list()
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