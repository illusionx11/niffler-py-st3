import allure
import logging
from http import HTTPStatus
from models.config import ServerEnvs
from utils.sessions import BaseSession

class UsersClient:
    
    session: BaseSession
    server_envs: ServerEnvs
    
    USERS_ENDPOINT = "/api/users"
    STAT_ENDPOINT = "/api/v2/stat"
    CURRENT_USER_ENDPOINT = "/api/users/current"
    UPDATE_USER_ENDPOINT = "/api/users/update"
    
    def __init__(self, server_envs: ServerEnvs, token: str):
        self.server_envs = server_envs
        self.session = BaseSession(base_url=server_envs.gateway_url)
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        })
        
    @allure.step("API Получение текущего пользователя")
    def get_current_user(self):
        try:
            res = self.session.get(url=self.CURRENT_USER_ENDPOINT)
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
            res = self.session.patch(
                url=self.UPDATE_USER_ENDPOINT, 
                json=data
            )
            if res.status_code == HTTPStatus.OK:
                logging.info(f"Имя профиля изменено на {name}")
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        except Exception as e:
            logging.error(f"Ошибка при обновлении профиля: {str(e)}", exc_info=True)
            assert False