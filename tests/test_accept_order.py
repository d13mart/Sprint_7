import pytest
import allure
import requests
from utils.courier_utils import generate_courier_data, delete_courier, login_courier, BASE_URL
from utils.order_utils import create_order, accept_order, get_order_by_track


@allure.epic("API Яндекс.Самокат")
@allure.feature("Принятие заказа")
class TestAcceptOrder:
    """Тесты для ручки PUT /api/v1/orders/accept/{orderId}"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Создаём курьера и заказ перед каждым тестом."""
        # Курьер
        courier_data = generate_courier_data()
        create_resp = requests.post(f"{BASE_URL}/courier", json=courier_data)
        assert create_resp.status_code == 201

        self.courier_login = courier_data["login"]
        self.courier_password = courier_data["password"]
        login_resp = login_courier(self.courier_login, self.courier_password)
        assert login_resp is not None
        self.courier_id = login_resp["id"]

        # Заказ
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
        
        # Получаем order_id (id заказа в базе) — с ретраями, т.к. заказ может не быть сразу доступен
        for _ in range(5):
            order = get_order_by_track(self.track)
            if order is not None:
                break
            import time
            time.sleep(0.5)
        else:
            pytest.fail(f"Заказ с track={self.track} не найден после создания")
        self.order_id = order["id"]

        yield

        # Чистим
        delete_courier(self.courier_id)
        requests.put(f"{BASE_URL}/orders/cancel", params={"track": self.track})

    @allure.title("Успешное принятие заказа курьером")
    def test_accept_order_success(self):
        """Успешный запрос возвращает {"ok": true}."""
        resp = accept_order(self.order_id, self.courier_id)
        assert resp is not None
        assert resp.get("ok") is True

    @allure.title("Ошибка если не передать id курьера")
    def test_accept_order_without_courier_id(self):
        """Если не передать id курьера — запрос вернёт ошибку."""
        resp = requests.put(f"{BASE_URL}/orders/accept/{self.order_id}")
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()

    @allure.title("Ошибка при неверном id курьера")
    def test_accept_order_with_wrong_courier_id(self):
        """Если передать неверный id курьера — запрос вернёт ошибку."""
        resp = accept_order(self.order_id, 99999999)
        assert resp is None  # вернётся None при ошибке 404

    @allure.title("Ошибка если не передать id заказа")
    def test_accept_order_without_order_id(self):
        """Если не передать id заказа — запрос вернёт ошибку."""
        resp = requests.put(f"{BASE_URL}/orders/accept/", params={"courierId": self.courier_id})
        assert resp.status_code in (404, 405)

    @allure.title("Ошибка при неверном id заказа")
    def test_accept_order_with_wrong_order_id(self):
        """Если передать неверный id заказа — запрос вернёт ошибку."""
        resp = accept_order(99999999, self.courier_id)
        assert resp is None