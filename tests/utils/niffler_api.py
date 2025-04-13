import os
import requests
import logging
from http import HTTPStatus
from tests.utils.generate_random_hex import generate_random_hex

class NifflerAPI:
    
    TOKEN_URL = f"{os.getenv('AUTH_URL')}/oauth2/token"
    CURRENCIES_URL = f"{os.getenv('GATEWAY_URL')}/api/currencies"
    USERS_URL = f"{os.getenv('GATEWAY_URL')}/api/users"
    STAT_URL = f"{os.getenv('GATEWAY_URL')}/api/v2/stat"
    SPENDS_URL = f"{os.getenv('GATEWAY_URL')}/api/v2/spends"
    ALL_SPENDS_URL = f"{SPENDS_URL}/all"
    ADD_SPENDS_URL = f"{os.getenv('GATEWAY_URL')}/api/spends/add"
    DELETE_SPENDS_URL = f"{os.getenv('GATEWAY_URL')}/api/spends/remove"
    ADD_CATEGORY_URL = f"{os.getenv('GATEWAY_URL')}/api/categories/add"
    UPDATE_CATEGORY_URL = f"{os.getenv('GATEWAY_URL')}/api/categories/update"
    GET_CATEGORIES_URL = f"{os.getenv('GATEWAY_URL')}/api/categories/all"
    CURRENT_USER_URL = f"{os.getenv('GATEWAY_URL')}/api/users/current"
    UPDATE_USER_URL = f"{os.getenv('GATEWAY_URL')}/api/users/update"
        
    def __init__(self, token: str, config: dict[str, str]):
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {token}"
        })
        self.config = config
        
    def register(self, username: str, password: str):
        try:
            _response = self.session.get(url=self.config["register_url"])
            _csrf_token = _response.cookies["XSRF-TOKEN"]
            data = {
                "username": username,
                "password": password,
                "passwordSubmit": password,
                "_csrf": _csrf_token,
            }
            res = self.session.post(url=self.config["register_url"], data=data)
            if res.status_code == HTTPStatus.CREATED:
                logging.info(f"Создан пользователь {username}")
            else:
                logging.info(f"Пользователь {username} уже существует")
        
        except Exception as e:
            logging.error(f"Ошибка при регистрации пользователя {username}: {str(e)}", exc_info=True)
            assert False
    
    def add_spending(self, data: dict):
        try:
            res = self.session.post(url=self.ADD_SPENDS_URL, json=data)
            if res.status_code == HTTPStatus.CREATED:
                data.update({"id": res.json()["id"]})
                logging.info(f"Трата добавлена. ID: {data['id']}")
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при добавлении траты: {str(e)}", exc_info=True)
            assert False
    
    def get_all_spendings(self) -> list[dict]:
        try:
            res = self.session.get(url=self.ALL_SPENDS_URL)
            if res.status_code == HTTPStatus.OK:
                return res.json()["content"]
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при получении всех трат: {str(e)}", exc_info=True)
            assert False
        
    def clear_all_spendings(self, ids: list[str] | None = None):
        try:
            if ids is None:
                all_spendings = self.get_all_spendings()
                ids = [r["id"] for r in all_spendings] if len(all_spendings) > 0 else []
            if len(ids) == 0:
                logging.info(f"Таблица трат пустая, удаление не требуется")
                return
            
            params = {
                "ids": ",".join(ids) if len(ids) > 1 else ids[0]
            }
            res = self.session.delete(url=self.DELETE_SPENDS_URL, params=params)
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Все траты удалены")
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
            
        except Exception as e:
            logging.error(f"Ошибка при удалении всех трат: {str(e)}", exc_info=True)
            assert False
            
    def add_category(self, category_name: str):
        try:
            data = {"name": category_name}
            res = self.session.post(url=self.ADD_CATEGORY_URL, json=data)
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Категория {category_name} добавлена")
                return res.json()
            elif res.status_code == HTTPStatus.CONFLICT:
                logging.info(f"Категория {category_name} уже существует")
                return self.get_category_by_name(category_name)
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при добавлении категории: {str(e)}", exc_info=True)
            assert False
            
    def get_all_categories(self, exclude_archived: bool = False):
        try:
            params = {
                "excludeArchived": exclude_archived
            }
            res = self.session.get(url=self.GET_CATEGORIES_URL, params=params)
            if res.status_code == HTTPStatus.OK:
                return res.json()
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при получении всех категорий: {str(e)}", exc_info=True)
            assert False
            
    def get_category_by_name(self, name: str):
        try:
            all_categories = self.get_all_categories()
            return next((c for c in all_categories if c["name"] == name), None)
        except Exception as e:
            logging.error(f"Ошибка при получении категории по имени: {str(e)}", exc_info=True)
            assert False
    
    def update_category(self, category_data: dict):
        try:
            res = self.session.patch(url=self.UPDATE_CATEGORY_URL, json=category_data)
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Категория {category_data['name']} обновлена")
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при обновлении категории: {str(e)}", exc_info=True)
            assert False
    
    def get_current_user(self):
        try:
            res = self.session.get(url=self.CURRENT_USER_URL)
            if res.status_code == HTTPStatus.OK:
                return res.json()
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при получении текущего пользователя: {str(e)}", exc_info=True)
            assert False
    
    def update_profile_name(self, name: str):
        current_user = self.get_current_user()
        data = {
            "fullname": name,
            "id": current_user["id"],
            "photo": "",
            "username": current_user["username"]
        }
        try:
            res = self.session.patch(url=self.UPDATE_USER_URL, json=data)
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Имя профиля изменено на {name}")
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при обновлении профиля: {str(e)}", exc_info=True)
            assert False
        
    def cleanup(self):
        all_categories = self.get_all_categories()
        for category_data in all_categories:
            if not category_data["name"].startswith("0033"):
                category_data["name"] = generate_random_hex()
            category_data["archived"] = True
            self.update_category(category_data)