import pytest
import allure
import requests
from config import BASE_URL
from api_client import api


@allure.epic("API Яндекс.Самокат")
@allure.feature("Получение заказа по номеру")
class TestGetOrderByTrack:
    """Тесты для ручки GET /api/v1/orders/track"""

    @pytest.fixture(autouse=True)
    def setup(self, created_order):
        """Подготовка заказа через фикстуру."""
        self.track = created_order["track"]

    @allure.title("Успешное получение заказа по треку")
    def test_get_order_by_track_success(self):
        """Успешный запрос возвращает объект с заказом."""
        # Ретраи внутри api.get_order_by_track
        order = api.get_order_by_track(self.track)
        assert order is not None, f"Заказ с track={self.track} не найден"
        assert order.get("track") == self.track
        assert "firstName" in order
        assert "lastName" in order
        assert "address" in order

    @allure.title("Ошибка при запросе без номера заказа")
    def test_get_order_without_track(self):
        """Запрос без номера заказа возвращает ошибку."""
        resp = requests.get(f"{BASE_URL}/orders/track", timeout=(10, 30))
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()

    @allure.title("Ошибка при запросе с несуществующим номером заказа")
    def test_get_order_with_nonexistent_track(self):
        """Запрос с несуществующим заказом возвращает ошибку."""
        resp = requests.get(
            f"{BASE_URL}/orders/track",
            params={"t": 99999999},
            timeout=(10, 30)
        )
        assert resp.status_code == 404
        assert "не найден" in resp.json().get("message", "").lower()