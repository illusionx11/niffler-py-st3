import allure
import logging
from models.config import ServerEnvs, ClientEnvs
from utils.sessions import AuthSession
from models.oauth import OAuthRequest
from http import HTTPStatus
import pkce
from requests import Response
from models.auth_user import TokenData

class OAuthClient:
    """Авторизует по Oauth2.0"""
    
    session: AuthSession
    server_envs: ServerEnvs
    
    REGISTER_ENDPOINT = "/register"
    AUTH_ENDPOINT = "/oauth2/authorize"
    AUTHORIZED_URI = "{frontend_url}/authorized"
    LOGIN_ENDPOINT = "/login"
    TOKEN_ENDPOINT = "/oauth2/token"
    
    def __init__(self, server_envs: ServerEnvs):
        """Генерируем code_verifier и code_challenge."""
        self.server_envs = server_envs
        self.session = AuthSession(base_url=server_envs.auth_url)
        self.code_verifier, self.code_challenge = pkce.generate_pkce_pair()
        self.token = None
        self.id_token = None
    
    @allure.step("API Регистрация пользователя")
    def register(self, username: str, password: str) -> Response:
        try:
            self.session.cookies.clear()
            self.session.headers.clear()
            response = self.session.get(url=self.REGISTER_ENDPOINT)
            csrf_token = response.cookies.get("XSRF-TOKEN")

            data = {
                "_csrf": csrf_token,
                "username": username,
                "password": password,
                "passwordSubmit": password
            }
            res = self.session.post(
                url=self.REGISTER_ENDPOINT, 
                data=data, 
                allow_redirects=True
            )
            if res.status_code == HTTPStatus.CREATED:
                logging.info(f"Создан пользователь {username}")
                return res
        
            elif res.status_code == 400:
                logging.info(f"Пользователь {username} уже существует")
                return res
            
            else:
                raise Exception(f"Код {res.status_code} | Text {res.text}")
        
        except Exception as e:
            err_text = f"Ошибка при регистрации пользователя {username}: {str(e)}"
            logging.error(err_text, exc_info=True)
            assert False, err_text
    
    @allure.step("API Авторизация и получение токена")
    def get_token(self, username: str, password: str) -> TokenData:
        """Возвращает access token для авторизации пользователя с username и password.
        
        1. Получаем jsessionid и xsrf-токен куку в сессию.
        2. Получаем code из redirect uri по xsrf-токену.
        3. Получаем access token.
        """
        self.session.get(
            url=self.AUTH_ENDPOINT,
            params=OAuthRequest(
                redirect_uri=self.AUTHORIZED_URI.format(frontend_url=self.server_envs.frontend_url),
                code_challenge=self.code_challenge
            ).model_dump(),
            allow_redirects=True
        )
        
        self.session.post(
            url=self.LOGIN_ENDPOINT,
            data={
                "_csrf": self.session.cookies.get("XSRF-TOKEN"),
                "username": username,
                "password": password,
            },
            allow_redirects=True
        )
        
        token_response = self.session.post(
            url=self.TOKEN_ENDPOINT,
            data={
                "code": self.session.code,
                "redirect_uri": self.AUTHORIZED_URI.format(frontend_url=self.server_envs.frontend_url),
                "code_verifier": self.code_verifier,
                "grant_type": "authorization_code",
                "client_id": "client"
            }
        )
        self.token = token_response.json().get("access_token", None)
        self.id_token = token_response.json().get("id_token", None)
        cookie_list = []
        for cookie in self.session.cookies:
            cookie_list.append({
                "name": cookie.name,
                "value": cookie.value,
                "path": cookie.path,
                "domain": cookie.domain,
                "secure": cookie.secure
            })
        
        logging.info("Получен access token")
        return TokenData(
            access_token=self.token,
            code_verifier=self.code_verifier,
            code_challenge=self.code_challenge,
            id_token=self.id_token,
            cookies=cookie_list
        )