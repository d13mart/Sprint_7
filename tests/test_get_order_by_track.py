import pytest
import allure
import requests
from utils.order_utils import create_order, get_order_by_track, BASE_URL


@allure.epic("API Яндекс.Самокат")
@allure.feature("Получение заказа по номеру")
class TestGetOrderByTrack:
    """Тесты для ручки GET /api/v1/orders/track"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Создаём заказ перед каждым тестом."""
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
        self.track = created["track"]

        yield

        # Чистим
        requests.put(f"{BASE_URL}/orders/cancel", params={"track": self.track})

    @allure.title("Успешное получение заказа по треку")
    def test_get_order_by_track_success(self):
        """Успешный запрос возвращает объект с заказом."""
        order = get_order_by_track(self.track)
        assert order is not None
        assert order.get("track") == self.track
        assert "firstName" in order
        assert "lastName" in order
        assert "address" in order

    @allure.title("Ошибка при запросе без номера заказа")
    def test_get_order_without_track(self):
        """Запрос без номера заказа возвращает ошибку."""
        resp = requests.get(f"{BASE_URL}/orders/track")
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()

    @allure.title("Ошибка при запросе с несуществующим номером заказа")
    def test_get_order_with_nonexistent_track(self):
        """Запрос с несуществующим заказом возвращает ошибку."""
        resp = requests.get(f"{BASE_URL}/orders/track", params={"t": 99999999})
        assert resp.status_code == 404
        assert "не найден" in resp.json().get("message", "").lower()