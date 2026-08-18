import pytest
import allure
import requests
from utils.courier_utils import generate_courier_data, delete_courier, login_courier, BASE_URL


@allure.epic("API Яндекс.Самокат")
@allure.feature("Логин курьера")
class TestCourierLogin:
    """Тесты для ручки POST /api/v1/courier/login"""

    @allure.title("Успешная авторизация курьера")
    def test_login_courier_success(self):
        """Курьер может авторизоваться с верными данными."""
        data = generate_courier_data()
        login, password, first_name = data["login"], data["password"], data["firstName"]

        # Сначала создаём курьера
        create_resp = requests.post(f"{BASE_URL}/courier", json=data)
        assert create_resp.status_code == 201

        # Логинимся
        resp = login_courier(login, password)
        assert resp is not None
        assert "id" in resp
        courier_id = resp["id"]
        assert isinstance(courier_id, int) and courier_id > 0

        # Чистим
        delete_courier(courier_id)

    @allure.title("Ошибка при неверном логине")
    def test_login_wrong_login(self):
        """Система вернёт ошибку, если указать несуществующий логин."""
        data = generate_courier_data()
        login, password, first_name = data["login"], data["password"], data["firstName"]

        # Создаём курьера
        create_resp = requests.post(f"{BASE_URL}/courier", json=data)
        assert create_resp.status_code == 201

        # Пытаемся зайти с неверным логином
        resp = requests.post(f"{BASE_URL}/courier/login", json={"login": "nonexistent_login", "password": password})
        assert resp.status_code == 404
        assert "не найден" in resp.json().get("message", "").lower()

        # Чистим
        login_resp = login_courier(login, password)
        if login_resp:
            delete_courier(login_resp["id"])

    @allure.title("Ошибка при неверном пароле")
    def test_login_wrong_password(self):
        """Система вернёт ошибку, если указать неверный пароль."""
        data = generate_courier_data()
        login, password, first_name = data["login"], data["password"], data["firstName"]

        # Создаём курьера
        create_resp = requests.post(f"{BASE_URL}/courier", json=data)
        assert create_resp.status_code == 201

        # Пытаемся зайти с неверным паролем
        resp = requests.post(f"{BASE_URL}/courier/login", json={"login": login, "password": "wrong_password"})
        assert resp.status_code == 404
        assert "не найден" in resp.json().get("message", "").lower()

        # Чистим
        login_resp = login_courier(login, password)
        if login_resp:
            delete_courier(login_resp["id"])

    @allure.title("Ошибка при отсутствии логина")
    def test_login_without_login(self):
        """Если не передать login — вернётся ошибка."""
        data = generate_courier_data()
        password = data["password"]

        # Создаём курьера
        create_resp = requests.post(f"{BASE_URL}/courier", json=data)
        assert create_resp.status_code == 201

        resp = requests.post(f"{BASE_URL}/courier/login", json={"password": password})
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()

        # Чистим
        login_resp = login_courier(data["login"], password)
        if login_resp:
            delete_courier(login_resp["id"])

    @allure.title("Ошибка при отсутствии пароля")
    def test_login_without_password(self):
        """Если не передать password — вернётся ошибка."""
        data = generate_courier_data()
        login = data["login"]

        # Создаём курьера
        create_resp = requests.post(f"{BASE_URL}/courier", json=data)
        assert create_resp.status_code == 201

        # Ретраи для сетевых флапов с увеличенным таймаутом
        resp = None
        for attempt in range(5):
            try:
                resp = requests.post(f"{BASE_URL}/courier/login", json={"login": login}, timeout=(10, 30))
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                import time
                time.sleep(2)
        else:
            pytest.fail("Сетевая ошибка при запросе логина после 5 попыток")

        assert resp is not None
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()

        # Чистим
        login_resp = login_courier(login, data["password"])
        if login_resp:
            delete_courier(login_resp["id"])

    @allure.title("Ошибка при авторизации несуществующего пользователя")
    def test_login_nonexistent_user(self):
        """Если авторизоваться под несуществующим пользователем — ошибка."""
        resp = requests.post(f"{BASE_URL}/courier/login", json={"login": "fake", "password": "fake"})
        assert resp.status_code == 404
        assert "не найден" in resp.json().get("message", "").lower()