import pytest
import allure
from api_client import api


@allure.epic("API Яндекс.Самокат")
@allure.feature("Создание заказа")
class TestCreateOrder:
    """Тесты для ручки POST /api/v1/orders"""

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
        order_data = {
            "first_name": "Тест",
            "last_name": "Тестов",
            "address": "ул. Тестовая, 1",
            "metro_station": 1,
            "phone": "+7 999 999 99 99",
            "rent_time": 3,
            "delivery_date": "2026-09-01",
            "comment": "Тестовый заказ",
        }

        resp = api.create_order(**order_data, color=color)
        assert resp is not None, f"Не удалось создать заказ с цветом {color_name}"
        assert "track" in resp
        assert isinstance(resp["track"], int) and resp["track"] > 0

        # Отменяем заказ для чистоты
        api.cancel_order(resp["track"])

    @allure.title("Ответ содержит track")
    def test_create_order_returns_track(self):
        """Тело ответа содержит track."""
        order_data = {
            "first_name": "Тест",
            "last_name": "Тестов",
            "address": "ул. Тестовая, 1",
            "metro_station": 1,
            "phone": "+7 999 999 99 99",
            "rent_time": 3,
            "delivery_date": "2026-09-01",
            "comment": "Тестовый заказ",
        }
        resp = api.create_order(**order_data, color=["BLACK"])
        assert resp is not None
        assert "track" in resp
        assert isinstance(resp["track"], int)

        # Чистим
        api.cancel_order(resp["track"])