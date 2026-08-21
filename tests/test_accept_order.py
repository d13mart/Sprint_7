import pytest
import allure
from api_client import api


@allure.epic("API Яндекс.Самокат")
@allure.feature("Принятие заказа")
class TestAcceptOrder:
    """Тесты для ручки PUT /api/v1/orders/accept/{orderId}"""

    @pytest.fixture(autouse=True)
    def setup(self, logged_in_courier, created_order):
        """Подготовка курьера и заказа через фикстуры."""
        self.courier_id = logged_in_courier["courier_id"]
        self.order_id = created_order["order_id"]
        self.track = created_order["track"]

    @allure.title("Успешное принятие заказа курьером")
    def test_accept_order_success(self):
        """Успешный запрос возвращает {"ok": true}."""
        resp = api.accept_order(self.order_id, self.courier_id)
        assert resp is not None
        assert resp.get("ok") is True

    @allure.title("Ошибка если не передать id курьера")
    def test_accept_order_without_courier_id(self):
        """Если не передать id курьера — запрос вернёт ошибку."""
        import requests
        from config import BASE_URL
        resp = requests.put(
            f"{BASE_URL}/orders/accept/{self.order_id}",
            timeout=(10, 30)
        )
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()

    @allure.title("Ошибка при неверном id курьера")
    def test_accept_order_with_wrong_courier_id(self):
        """Если передать неверный id курьера — запрос вернёт ошибку."""
        resp = api.accept_order(self.order_id, 99999999)
        assert resp is None

    @allure.title("Ошибка если не передать id заказа")
    def test_accept_order_without_order_id(self):
        """Если не передать id заказа — запрос вернёт ошибку."""
        import requests
        from config import BASE_URL
        resp = requests.put(
            f"{BASE_URL}/orders/accept/",
            params={"courierId": self.courier_id},
            timeout=(10, 30)
        )
        assert resp.status_code in (404, 405)

    @allure.title("Ошибка при неверном id заказа")
    def test_accept_order_with_wrong_order_id(self):
        """Если передать неверный id заказа — запрос вернёт ошибку."""
        resp = api.accept_order(99999999, self.courier_id)
        assert resp is None