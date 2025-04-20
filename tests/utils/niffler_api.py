import os
import requests
from requests import Response
from requests_toolbelt.utils.dump import dump_response
import allure
import logging
from http import HTTPStatus
from tests.models.config import Envs
from tests.models.spend import Category, SpendGet, SpendAdd

class NifflerAPI:
           
    def __init__(self, envs: Envs):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
        self.envs = envs
        self.generate_endpoints()
        self.session.hooks["response"].append(self.attach_response)
        logging.info(f"Niffler API initialized.")
    
    @staticmethod
    def attach_response(response: Response, *args, **kwargs):
        attachment_name = response.request.method + " " + response.request.url
        allure.attach(dump_response(response), attachment_name, attachment_type=allure.attachment_type.TEXT)
    
    @allure.step("API Генерация Endpoint-ов")
    def generate_endpoints(self):
        
        self.token_endpoint = f"{self.envs.auth_url}/oauth2/token"
        self.currencies_endpoint = f"{self.envs.gateway_url}/api/currencies"
        self.users_endpoint = f"{self.envs.gateway_url}/api/users"
        self.stat_endpoint = f"{self.envs.gateway_url}/api/v2/stat"
        self.spends_endpoint = f"{self.envs.gateway_url}/api/v2/spends"
        self.all_spends_endpoint = f"{self.spends_endpoint}/all"
        self.add_spends_endpoint = f"{self.envs.gateway_url}/api/spends/add"
        self.delete_spends_endpoint = f"{self.envs.gateway_url}/api/spends/remove"
        self.add_category_endpoint = f"{self.envs.gateway_url}/api/categories/add"
        self.update_category_endpoint = f"{self.envs.gateway_url}/api/categories/update"
        self.get_categories_endpoint = f"{self.envs.gateway_url}/api/categories/all"
        self.current_user_endpoint = f"{self.envs.gateway_url}/api/users/current"
        self.update_user_endpoint = f"{self.envs.gateway_url}/api/users/update"
    
    @allure.step("API Регистрация пользователя")
    def register(self, username: str | None = None, password: str | None = None):
        try:
            _response = self.session.get(url=f"{self.envs.auth_url}/register")
            _csrf_token = _response.cookies["XSRF-TOKEN"]
            username = username if username else self.envs.test_username
            password = password if password else self.envs.test_password
            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "max-age=0",
                "content-type": "application/x-www-form-urlencoded",
                "upgrade-insecure-requests": "1"
            }
            data = {
                "_csrf": _csrf_token,
                "username": username,
                "password": password,
                "passwordSubmit": password
            }
            res = self.session.post(url=f"{self.envs.auth_url}/register", headers=headers, data=data, allow_redirects=True)
            if res.status_code == HTTPStatus.CREATED:
                logging.info(f"Создан пользователь {username}")
            elif res.status_code == 400:
                logging.info(f"Пользователь {username} уже существует")
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        
        except Exception as e:
            logging.error(f"Ошибка при регистрации пользователя {username}: {str(e)}", exc_info=True)
            assert False
    
    @allure.step("API Добавление траты")
    def add_spending(self, data: SpendAdd) -> SpendGet:
        try:
            if not data.username:
                data.username = self.envs.test_username
            res = self.session.post(url=self.add_spends_endpoint, json=data.model_dump())
            if res.status_code == HTTPStatus.CREATED:
                result = SpendGet.model_validate(res.json())
                logging.info(f"Трата добавлена. ID: {result.id}")
                return result
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при добавлении траты: {str(e)}", exc_info=True)
            assert False
    
    @allure.step("API Получение списка трат")
    def get_all_spendings(self) -> list[SpendGet]:
        try:
            res = self.session.get(url=self.all_spends_endpoint, params={"size": 1000})
            if res.status_code == HTTPStatus.OK:
                user_items = [item for item in res.json()["content"]]
                if len(user_items) == 0:
                    return []
                return [SpendGet.model_validate(item) for item in user_items]
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при получении всех трат: {str(e)}", exc_info=True)
            assert False
    
    @allure.step("API Удаление трат")
    def clear_spendings(self, ids: list[str] | None = None):
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
            res = self.session.delete(url=self.delete_spends_endpoint, params=params)
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Все траты удалены")
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
            
        except Exception as e:
            logging.error(f"Ошибка при удалении всех трат: {str(e)}", exc_info=True)
            assert False
    
    @allure.step("API Добавление категории")    
    def add_category(self, category_name: str) -> Category:
        try:
            data = {"name": category_name}
            res = self.session.post(url=self.add_category_endpoint, json=data)
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Категория {category_name} добавлена")
                return Category.model_validate(res.json())
            elif res.status_code == HTTPStatus.CONFLICT:
                logging.info(f"Категория {category_name} уже существует")
                return self.get_category_by_name(category_name)
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при добавлении категории: {str(e)}", exc_info=True)
            assert False
    
    @allure.step("API Получение списка категорий")   
    def get_all_categories(self, exclude_archived: bool = False) -> list[Category]:
        try:
            params = {
                "excludeArchived": exclude_archived
            }
            res = self.session.get(url=self.get_categories_endpoint, params=params)
            if res.status_code == HTTPStatus.OK:
                return [Category.model_validate(item) for item in res.json()]
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при получении категорий: {str(e)}", exc_info=True)
            assert False
    
    @allure.step("API Получение категории по имени")  
    def get_category_by_name(self, name: str) -> Category:
        try:
            all_categories = self.get_all_categories()
            result = next((c for c in all_categories if c["name"] == name), None)
            return Category.model_validate(result) if result else result

        except Exception as e:
            logging.error(f"Ошибка при получении категории по имени: {str(e)}", exc_info=True)
            assert False
    
    @allure.step("API Обновление категории")
    def update_category(self, category_data: Category):
        try:
            res = self.session.patch(url=self.update_category_endpoint, json=category_data.model_dump())
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Категория {category_data.name} обновлена")
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при обновлении категории: {str(e)}", exc_info=True)
            assert False
    
    @allure.step("API Получение текущего пользователя")
    def get_current_user(self):
        try:
            res = self.session.get(url=self.current_user_endpoint)
            if res.status_code == HTTPStatus.OK:
                return res.json()
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при получении текущего пользователя: {str(e)}", exc_info=True)
            assert False
    
    @allure.step("API Обновление имени профиля")
    def update_profile_name(self, name: str):
        current_user = self.get_current_user()
        data = {
            "fullname": name,
            "id": current_user["id"],
            "photo": "",
            "username": current_user["username"]
        }
        try:
            res = self.session.patch(url=self.update_user_endpoint, json=data)
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Имя профиля изменено на {name}")
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при обновлении профиля: {str(e)}", exc_info=True)
            assert False