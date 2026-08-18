import pytest
import allure
import requests
from utils.courier_utils import generate_courier_data, register_new_courier, delete_courier, login_courier, BASE_URL


@allure.epic("API Яндекс.Самокат")
@allure.feature("Создание курьера")
class TestCreateCourier:
    """Тесты для ручки POST /api/v1/courier"""

    @allure.title("Успешное создание курьера с валидными данными")
    def test_create_courier_success(self):
        """Курьера можно создать с валидными данными."""
        data = generate_courier_data()
        login, password, first_name = data["login"], data["password"], data["firstName"]

        # Проверяем, что курьер создался (код 201 и ok: true)
        resp = requests.post(f"{BASE_URL}/courier", json={
            "login": login,
            "password": password,
            "firstName": first_name
        })
        assert resp.status_code == 201
        assert resp.json().get("ok") is True

        # Чистим
        login_resp = login_courier(login, password)
        if login_resp:
            delete_courier(login_resp["id"])

    @allure.title("Нельзя создать двух одинаковых курьеров")
    def test_create_duplicate_courier_fails(self):
        """Нельзя создать двух курьеров с одинаковым логином."""
        data = generate_courier_data()
        login, password, first_name = data["login"], data["password"], data["firstName"]

        # Первый запрос — успех
        resp1 = requests.post(f"{BASE_URL}/courier", json={
            "login": login, "password": password, "firstName": first_name
        })
        assert resp1.status_code == 201

        # Второй запрос с теми же данными — ошибка 409
        resp2 = requests.post(f"{BASE_URL}/courier", json={
            "login": login, "password": password, "firstName": first_name
        })
        assert resp2.status_code == 409
        assert "уже используется" in resp2.json().get("message", "")

        # Чистим
        login_resp = login_courier(login, password)
        if login_resp:
            delete_courier(login_resp["id"])

    @allure.title("Ошибка при отсутствии обязательного поля: login")
    def test_create_courier_without_login(self):
        """Если не передать login — вернётся ошибка."""
        data = generate_courier_data()
        password, first_name = data["password"], data["firstName"]

        resp = requests.post(f"{BASE_URL}/courier", json={
            "password": password,
            "firstName": first_name
        })
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()

    @allure.title("Ошибка при отсутствии обязательного поля: password")
    def test_create_courier_without_password(self):
        """Если не передать password — вернётся ошибка."""
        data = generate_courier_data()
        login, first_name = data["login"], data["firstName"]

        resp = requests.post(f"{BASE_URL}/courier", json={
            "login": login,
            "firstName": first_name
        })
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()

    @allure.title("firstName не является обязательным полем")
    def test_create_courier_without_first_name(self):
        """firstName не обязателен — курьер создаётся без него."""
        data = generate_courier_data()
        login, password = data["login"], data["password"]

        resp = requests.post(f"{BASE_URL}/courier", json={
            "login": login,
            "password": password
        })
        # API позволяет создавать курьера без firstName
        assert resp.status_code == 201
        assert resp.json().get("ok") is True

        # Чистим
        login_resp = login_courier(login, password)
        if login_resp:
            delete_courier(login_resp["id"])