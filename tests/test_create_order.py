import pytest
import allure
import requests
from utils.order_utils import create_order, BASE_URL


@allure.epic("API Яндекс.Самокат")
@allure.feature("Создание заказа")
class TestCreateOrder:
    """Тесты для ручки POST /api/v1/orders"""

    # Базовые валидные данные для заказа
    BASE_ORDER_DATA = {
        "first_name": "Иван",
        "last_name": "Иванов",
        "address": "ул. Ленина, 1",
        "metro_station": 1,
        "phone": "+7 999 999 99 99",
        "rent_time": 5,
        "delivery_date": "2026-09-01",
        "comment": "Позвоните за час",
    }

    @pytest.mark.parametrize("color, color_name", [
        (["BLACK"], "BLACK"),
        (["GREY"], "GREY"),
        (["BLACK", "GREY"], "BLACK и GREY"),
        ([], "без цвета"),
        (None, "не указан цвет"),
    ])
    @allure.title("Создание заказа с цветом: {color_name}")
    def test_create_order_with_color(self, color, color_name):
        """Можно создать заказ с разными вариантами цвета."""
        data = self.BASE_ORDER_DATA.copy()

        resp = create_order(**data, color=color)
        assert resp is not None, f"Не удалось создать заказ с цветом {color_name}"
        assert "track" in resp
        assert isinstance(resp["track"], int) and resp["track"] > 0

        # Отменяем заказ для чистоты
        requests.put(f"{BASE_URL}/orders/cancel", params={"track": resp["track"]})

    @allure.title("Ответ содержит track")
    def test_create_order_returns_track(self):
        """Тело ответа содержит track."""
        data = self.BASE_ORDER_DATA.copy()
        resp = create_order(**data, color=["BLACK"])
        assert resp is not None
        assert "track" in resp
        assert isinstance(resp["track"], int)

        # Чистим
        requests.put(f"{BASE_URL}/orders/cancel", params={"track": resp["track"]})