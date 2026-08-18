import pytest
import allure
import requests
from utils.courier_utils import generate_courier_data, delete_courier, login_courier, BASE_URL


@allure.epic("API Яндекс.Самокат")
@allure.feature("Удаление курьера")
class TestDeleteCourier:
    """Тесты для ручки DELETE /api/v1/courier/{id}"""

    @allure.title("Успешное удаление курьера")
    def test_delete_courier_success(self):
        """Успешный запрос возвращает {"ok": true}."""
        data = generate_courier_data()
        # Создаём курьера
        create_resp = requests.post(f"{BASE_URL}/courier", json=data)
        assert create_resp.status_code == 201

        # Логинимся, чтобы получить id
        login_resp = login_courier(data["login"], data["password"])
        assert login_resp is not None
        courier_id = login_resp["id"]

        # Удаляем
        resp = requests.delete(f"{BASE_URL}/courier/{courier_id}")
        assert resp.status_code == 200
        assert resp.json().get("ok") is True

    @allure.title("Ошибка при удалении без id")
    def test_delete_courier_without_id(self):
        """Если отправить запрос без id — вернётся ошибка."""
        # Попытка удалить без id (невалидный URL)
        resp = requests.delete(f"{BASE_URL}/courier/")
        # Ожидаем 404 (Not Found) или 405 (Method Not Allowed) - эндпоинт не существует
        assert resp.status_code in (404, 405)

    @allure.title("Ошибка при удалении несуществующего id")
    def test_delete_nonexistent_courier(self):
        """Если отправить запрос с несуществующим id — вернётся ошибка."""
        resp = requests.delete(f"{BASE_URL}/courier/99999999")
        assert resp.status_code == 404
        assert "нет" in resp.json().get("message", "").lower()

    @allure.title("Ошибка при повторном удалении того же курьера")
    def test_delete_courier_twice(self):
        """Повторное удаление уже удалённого курьера возвращает ошибку."""
        data = generate_courier_data()
        # Создаём курьера
        create_resp = requests.post(f"{BASE_URL}/courier", json=data)
        assert create_resp.status_code == 201

        login_resp = login_courier(data["login"], data["password"])
        assert login_resp is not None
        courier_id = login_resp["id"]

        # Первый раз удаляем успешно
        resp1 = requests.delete(f"{BASE_URL}/courier/{courier_id}")
        assert resp1.status_code == 200

        # Второй раз — ошибка
        resp2 = requests.delete(f"{BASE_URL}/courier/{courier_id}")
        assert resp2.status_code == 404
        assert "нет" in resp2.json().get("message", "").lower()