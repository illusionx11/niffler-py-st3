import os
import requests
import logging
from http import HTTPStatus
from tests.pages.urls import Urls

class NifflerAPI:
    
    class Endpoints:
        TOKEN_URL = f"{os.getenv('AUTH_URL')}/oauth2/token"
        CURRENCIES_URL = f"{os.getenv('GATEWAY_URL')}/api/currencies"
        USERS_URL = f"{os.getenv('GATEWAY_URL')}/api/users"
        STAT_URL = f"{os.getenv('GATEWAY_URL')}/api/v2/stat"
        SPENDS_URL = f"{os.getenv('GATEWAY_URL')}/api/v2/spends"
        ALL_SPENDS_URL = f"{SPENDS_URL}/all"
        ADD_SPENDS_URL = f"{os.getenv('GATEWAY_URL')}/api/spends/add"
        DELETE_SPENDS_URL = f"{os.getenv('GATEWAY_URL')}/api/spends/remove"
        
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "Content-Type": "application/json",
        }
    
    def set_token(self, token: str):
        self.token = token
        self.headers.update({"Authorization": f"Bearer {self.token}"})
        
    def register(self, username: str, password: str):
        try:
            _response = self.session.get(url=Urls.REGISTER_URL)
            _csrf_token = _response.cookies["XSRF-TOKEN"]
            data = {
                "username": username,
                "password": password,
                "passwordSubmit": password,
                "_csrf": _csrf_token,
            }
            res = self.session.post(url=Urls.REGISTER_URL, data=data)
            if res.status_code == HTTPStatus.CREATED:
                logging.info(f"Создан пользователь {username}")
            else:
                logging.info(f"Пользователь {username} уже существует")
        
        except Exception as e:
            logging.error(f"Ошибка при регистрации пользователя {username}: {str(e)}", exc_info=True)
            assert False
    
    def add_spending(self, data: dict):
        try:
            res = self.session.post(url=self.Endpoints.ADD_SPENDS_URL, json=data, headers=self.headers)
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
            res = self.session.get(url=self.Endpoints.ALL_SPENDS_URL, headers=self.headers)
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
            res = self.session.delete(url=self.Endpoints.DELETE_SPENDS_URL, params=params, headers=self.headers)
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Все траты удалены")
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
            
        except Exception as e:
            logging.error(f"Ошибка при удалении всех трат: {str(e)}", exc_info=True)
            assert False