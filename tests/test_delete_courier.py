import pytest
import allure
from api_client import api


@allure.epic("API Яндекс.Самокат")
@allure.feature("Удаление курьера")
class TestDeleteCourier:
    """Тесты для ручки DELETE /api/v1/courier/{id}"""

    @allure.title("Успешное удаление курьера")
    def test_delete_courier_success(self, logged_in_courier):
        """Успешный запрос возвращает {"ok": true}."""
        courier_id = logged_in_courier["courier_id"]
        result = api.delete_courier(courier_id)
        assert result is True
        # logged_in_courier fixture already cleans up, but we already deleted it
        # The fixture will try to delete again, which will return 404 - that's fine

    @allure.title("Ошибка при удалении без id")
    def test_delete_courier_without_id(self):
        """Если отправить запрос без id — вернётся ошибка."""
        import requests
        from config import BASE_URL
        resp = requests.delete(f"{BASE_URL}/courier/", timeout=(10, 30))
        assert resp.status_code in (404, 405)

    @allure.title("Ошибка при удалении несуществующего id")
    def test_delete_nonexistent_courier(self):
        """Если отправить запрос с несуществующим id — вернётся ошибка."""
        result = api.delete_courier(99999999)
        assert result is False

    @allure.title("Ошибка при повторном удалении того же курьера")
    def test_delete_courier_twice(self, logged_in_courier):
        """Повторное удаление уже удалённого курьера возвращает ошибку."""
        courier_id = logged_in_courier["courier_id"]
        # Первый раз удаляем успешно
        result1 = api.delete_courier(courier_id)
        assert result1 is True
        # Второй раз — ошибка
        result2 = api.delete_courier(courier_id)
        assert result2 is False