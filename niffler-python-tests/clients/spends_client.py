import allure
import logging
from http import HTTPStatus
from models.config import ServerEnvs, ClientEnvs
from models.spend import SpendGet, SpendAdd
from models.category import Category, CategoryAdd
from utils.sessions import BaseSession

class SpendsClient:
    
    session: BaseSession
    server_envs: ServerEnvs
    client_envs: ClientEnvs
    
    SPENDS_ENDPOINT = "/api/v2/spends"
    ALL_SPENDS_ENDPOINT = "/api/v2/spends/all"
    GET_SPEND_BY_ID_ENDPOINT = "/api/spends/{id}"
    EDIT_SPEND_ENDPOINT = "/api/spends/edit"
    ADD_SPENDS_ENDPOINT = "/api/spends/add"
    DELETE_SPENDS_ENDPOINT = "/api/spends/remove"
    
    ADD_CATEGORY_ENDPOINT = "/api/categories/add"
    UPDATE_CATEGORY_ENDPOINT = "/api/categories/update"
    GET_CATEGORIES_ENDPOINT = "/api/categories/all"
    
    CURRENCIES_ENDPOINT = "/api/currencies"
    
    def __init__(self, server_envs: ServerEnvs, client_envs: ClientEnvs, token: str):
        self.server_envs = server_envs
        self.client_envs = client_envs
        self.session = BaseSession(base_url=server_envs.gateway_url)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        })
        
    @allure.step("API Добавление траты")
    def add_spending(self, data: SpendAdd) -> SpendGet:
        try:
            if not data.username:
                data.username = self.client_envs.test_username
            res = self.session.post(
                url=self.ADD_SPENDS_ENDPOINT, 
                json=data.model_dump()
            )
            if res.status_code == HTTPStatus.CREATED:
                result = SpendGet.model_validate(res.json())
                logging.info(f"Трата добавлена. ID: {result.id}")
                return result
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при добавлении траты: {str(e)}", exc_info=True)
            assert False, str(e)
    
    @allure.step("API Получение списка трат")
    def get_all_spendings(self) -> list[SpendGet]:
        try:
            res = self.session.get(
                url=self.ALL_SPENDS_ENDPOINT, 
                params={"size": 1000}
            )
            if res.status_code == HTTPStatus.OK:
                user_items = [item for item in res.json()["content"]]
                if len(user_items) == 0:
                    return []
                return [SpendGet.model_validate(item) for item in user_items]
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при получении всех трат: {str(e)}", exc_info=True)
            assert False, str(e)
    
    @allure.step("API Получение траты по ID")
    def get_spending_by_id(self, id: str) -> SpendGet:
        try:
            res = self.session.get(
                url=self.GET_SPEND_BY_ID_ENDPOINT.format(id=id)
            )
            if res.status_code == HTTPStatus.OK:
                return SpendGet.model_validate(res.json())
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при получении траты по ID: {str(e)}", exc_info=True)
            assert False, str(e)
    
    @allure.step("API Редактирование траты")
    def update_spending(self, data: SpendAdd) -> SpendGet:
        try:
            res = self.session.patch(
                url=self.EDIT_SPEND_ENDPOINT, 
                json=data.model_dump()
            )
            if res.status_code == HTTPStatus.OK:
                return SpendGet.model_validate(res.json())
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при обновлении траты: {str(e)}", exc_info=True)
            assert False, str(e)
    
    @allure.step("API Удаление трат")
    def clear_spendings(self, ids: list[str] | None = None):
        """Удаление трат без возврата ответа.
        Но, если надо проверить саму ручку удаления, то надо добавить возврат response.
        """
        try:
            if ids is None:
                all_spendings = self.get_all_spendings()
                ids = [r.id for r in all_spendings] if len(all_spendings) > 0 else []
            if len(ids) == 0:
                logging.info(f"Таблица трат пустая, удаление не требуется")
                return
            
            params = {
                "ids": ",".join(ids) if len(ids) > 1 else ids[0]
            }
            logging.info(f"Удаление трат: {ids}")
            res = self.session.delete(
                url=self.DELETE_SPENDS_ENDPOINT, 
                params=params
            )
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Все траты удалены")
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
            
        except Exception as e:
            logging.error(f"Ошибка при удалении всех трат: {str(e)}", exc_info=True)
            assert False, str(e)
            
    @allure.step("API Добавление категории")    
    def add_category(self, category_name: str) -> Category | dict:
        try:
            data = {"name": category_name}
            res = self.session.post(
                url=self.ADD_CATEGORY_ENDPOINT, 
                json=data
            )
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Категория {category_name} добавлена")
                return Category.model_validate(res.json())
            elif res.status_code == HTTPStatus.CONFLICT:
                logging.info(f"Категория {category_name} уже существует")
                return res.json()
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при добавлении категории: {str(e)}", exc_info=True)
            assert False, str(e)
    
    @allure.step("API Получение списка категорий")   
    def get_all_categories(self, exclude_archived: bool = False) -> list[Category]:
        try:
            params = {
                "excludeArchived": "false" if exclude_archived == False else "true"
            }
            res = self.session.get(
                url=self.GET_CATEGORIES_ENDPOINT, 
                params=params
            )
            if res.status_code == HTTPStatus.OK:
                return [Category.model_validate(item) for item in res.json()]
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при получении категорий: {str(e)}", exc_info=True)
            assert False, str(e)
    
    @allure.step("API Получение категории по имени")  
    def get_category_by_name(self, name: str) -> Category:
        try:
            all_categories = self.get_all_categories()
            result = next((c for c in all_categories if c.name == name), None)
            return Category.model_validate(result) if result else result

        except Exception as e:
            logging.error(f"Ошибка при получении категории по имени: {str(e)}", exc_info=True)
            assert False
    
    @allure.step("API Обновление категории")
    def update_category(self, category_data: Category) -> Category:
        try:
            res = self.session.patch(
                url=self.UPDATE_CATEGORY_ENDPOINT, 
                json=category_data.model_dump()
            )
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Категория {category_data.name} обновлена")
                return Category.model_validate(res.json())
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при обновлении категории: {str(e)}", exc_info=True)
            assert False, str(e)