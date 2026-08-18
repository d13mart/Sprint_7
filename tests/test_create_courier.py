import pytest
import allure
from api_client import api


@allure.epic("API Яндекс.Самокат")
@allure.feature("Создание курьера")
class TestCreateCourier:
    """Тесты для ручки POST /api/v1/courier"""

    @allure.title("Успешное создание курьера с валидными данными")
    def test_create_courier_success(self, courier_data):
        """Курьера можно создать с валидными данными."""
        resp = api.create_courier(
            courier_data["login"],
            courier_data["password"],
            courier_data["firstName"]
        )
        assert resp is not None
        assert resp.get("ok") is True
        
        # Чистим - получаем id через логин
        login_resp = api.login_courier(courier_data["login"], courier_data["password"])
        if login_resp:
            api.delete_courier(login_resp["id"])

    @allure.title("Нельзя создать двух одинаковых курьеров")
    def test_create_duplicate_courier_fails(self, courier_data):
        """Нельзя создать двух курьеров с одинаковым логином."""
        # Первый запрос — успех
        resp1 = api.create_courier(
            courier_data["login"],
            courier_data["password"],
            courier_data["firstName"]
        )
        assert resp1 is not None

        # Второй запрос с теми же данными — ошибка 409
        resp2 = api.create_courier(
            courier_data["login"],
            courier_data["password"],
            courier_data["firstName"]
        )
        # create_courier возвращает None при ошибке, проверяем через прямой запрос
        import requests
        from config import BASE_URL
        resp2_raw = requests.post(
            f"{BASE_URL}/courier",
            json={
                "login": courier_data["login"],
                "password": courier_data["password"],
                "firstName": courier_data["firstName"]
            }
        )
        assert resp2_raw.status_code == 409
        assert "уже используется" in resp2_raw.json().get("message", "")

        # Чистим
        login_resp = api.login_courier(courier_data["login"], courier_data["password"])
        if login_resp:
            api.delete_courier(login_resp["id"])

    @allure.title("Ошибка при отсутствии обязательного поля: login")
    def test_create_courier_without_login(self, courier_data):
        """Если не передать login — вернётся ошибка."""
        import requests
        from config import BASE_URL
        resp = requests.post(
            f"{BASE_URL}/courier",
            json={
                "password": courier_data["password"],
                "firstName": courier_data["firstName"]
            }
        )
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()

    @allure.title("Ошибка при отсутствии обязательного поля: password")
    def test_create_courier_without_password(self, courier_data):
        """Если не передать password — вернётся ошибка."""
        import requests
        from config import BASE_URL
        resp = requests.post(
            f"{BASE_URL}/courier",
            json={
                "login": courier_data["login"],
                "firstName": courier_data["firstName"]
            }
        )
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()

    @allure.title("firstName не является обязательным полем")
    def test_create_courier_without_first_name(self, courier_data):
        """firstName не обязателен — курьер создаётся без него."""
        resp = api.create_courier(
            courier_data["login"],
            courier_data["password"],
            ""  # пустой firstName
        )
        # API позволяет создавать курьера без firstName
        assert resp is not None
        assert resp.get("ok") is True

        # Чистим
        login_resp = api.login_courier(courier_data["login"], courier_data["password"])
        if login_resp:
            api.delete_courier(login_resp["id"])