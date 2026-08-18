import pytest
import allure
from api_client import api


@allure.epic("API Яндекс.Самокат")
@allure.feature("Логин курьера")
class TestCourierLogin:
    """Тесты для ручки POST /api/v1/courier/login"""

    @allure.title("Успешная авторизация курьера")
    def test_login_courier_success(self, created_courier):
        """Курьер может авторизоваться с верными данными."""
        resp = api.login_courier(created_courier["login"], created_courier["password"])
        assert resp is not None
        assert "id" in resp
        courier_id = resp["id"]
        assert isinstance(courier_id, int) and courier_id > 0
        # created_courier fixture already cleans up

    @allure.title("Ошибка при неверном логине")
    def test_login_wrong_login(self, created_courier):
        """Система вернёт ошибку, если указать несуществующий логин."""
        import requests
        from config import BASE_URL
        resp = requests.post(
            f"{BASE_URL}/courier/login",
            json={"login": "nonexistent_login", "password": created_courier["password"]},
            timeout=(10, 30)
        )
        assert resp.status_code == 404
        assert "не найден" in resp.json().get("message", "").lower()
        # created_courier fixture already cleans up

    @allure.title("Ошибка при неверном пароле")
    def test_login_wrong_password(self, created_courier):
        """Система вернёт ошибку, если указать неверный пароль."""
        import requests
        from config import BASE_URL
        resp = requests.post(
            f"{BASE_URL}/courier/login",
            json={"login": created_courier["login"], "password": "wrong_password"},
            timeout=(10, 30)
        )
        assert resp.status_code == 404
        assert "не найден" in resp.json().get("message", "").lower()
        # created_courier fixture already cleans up

    @allure.title("Ошибка при отсутствии логина")
    def test_login_without_login(self, created_courier):
        """Если не передать login — вернётся ошибка."""
        import requests
        from config import BASE_URL
        resp = requests.post(
            f"{BASE_URL}/courier/login",
            json={"password": created_courier["password"]},
            timeout=(10, 30)
        )
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()
        # created_courier fixture already cleans up

    @allure.title("Ошибка при отсутствии пароля")
    def test_login_without_password(self, created_courier):
        """Если не передать password — вернётся ошибка."""
        import requests
        from config import BASE_URL
        
        # Ретраи для сетевых флапов (API иногда зависает на этом запросе)
        resp = None
        for attempt in range(5):
            try:
                resp = requests.post(
                    f"{BASE_URL}/courier/login",
                    json={"login": created_courier["login"]},
                    timeout=(10, 30)
                )
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
                import time
                time.sleep(2)
        else:
            pytest.fail("Сетевая ошибка при запросе логина после 5 попыток")

        assert resp is not None
        assert resp.status_code == 400
        assert "недостаточно данных" in resp.json().get("message", "").lower()
        # created_courier fixture already cleans up

    @allure.title("Ошибка при авторизации несуществующего пользователя")
    def test_login_nonexistent_user(self):
        """Если авторизоваться под несуществующим пользователем — ошибка."""
        import requests
        from config import BASE_URL
        resp = requests.post(
            f"{BASE_URL}/courier/login",
            json={"login": "fake", "password": "fake"},
            timeout=(10, 30)
        )
        assert resp.status_code == 404
        assert "не найден" in resp.json().get("message", "").lower()