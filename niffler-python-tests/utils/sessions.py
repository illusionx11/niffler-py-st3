import requests
from requests import Session, Response
from urllib.parse import urlparse, parse_qs
import allure
from requests_toolbelt.utils.dump import dump_response
import curlify
import json
from json import JSONDecodeError
import logging 

def raise_for_status(response: Response):
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        # если пользователь уже зарегистрирован, сервер возвращает 400. Поэтому данный сценарий - исключение для условия ниже
        if "register" not in response.request.url and response.status_code == 400:
            raise requests.HTTPError(f"{str(e)}: {response.text}") from e

def allure_attach_request(function):
    """Декоратор логирования запроса, хедеров запроса, ответа, хедеров ответа в allure шаг и allure attachment, а также в консоль."""
    def wrapper(*args, **kwargs):
        method, url = args[1], args[2]
        with allure.step(f"{method} {url}"):
            response: Response = function(*args, **kwargs)
            curl = curlify.to_curl(response.request)
            logging.debug(curl)
            logging.debug(response.text)
            allure.attach(
                body=curl, 
                name="Request", 
                attachment_type=allure.attachment_type.TEXT, 
                extension=".txt"
            )
            try:
                allure.attach(
                    body=json.dumps(response.json(), indent=4).encode("utf-8"), 
                    name=f"Response json {response.status_code}", 
                    attachment_type=allure.attachment_type.JSON, 
                    extension=".json"
                )
            except JSONDecodeError:
                allure.attach(
                    body=response.text.encode("utf-8"), 
                    name=f"Response text {response.status_code}", 
                    attachment_type=allure.attachment_type.TEXT, 
                    extension=".txt"
                )
            allure.attach(
                body=json.dumps(dict(response.headers), indent=4).encode("utf-8"), 
                name=f"Response headers {response.status_code}", 
                attachment_type=allure.attachment_type.JSON, 
                extension=".json"
            )
        raise_for_status(response)    
        return response
    return wrapper

class BaseSession(Session):
    """Сессия с прокидыванием base_url и логированием запроса, ответа, хэдеров ответа, хэдеров запроса."""
    def __init__(self, *args, **kwargs):
        """Прокидываем base_url - url авторизации из энвов"""
        super().__init__()
        self.base_url = kwargs.pop("base_url", "")
        
    @allure_attach_request
    def request(self, method, url, **kwargs) -> Response:
        """Логирование запроса и вклейка base_url."""
        return super().request(method, self.base_url + url, **kwargs)
        
class AuthSession(Session):
    """Сессия прокидыванием base_url и логированием запроса, ответа, хэдеров ответа, хэдеров запроса.
    + Автосохранение cookies внутри сессии из каждого response и redirect response, и 'code'."""
    def __init__(self, *args, **kwargs):
        """
        Прокидываем base_url - url авторизации из энвов
        code - код авторизации из redirect_uri
        """
        super().__init__()
        self.base_url = kwargs.pop("base_url", "")
        self.code: str | None = None
    
    @allure_attach_request
    def request(self, method, url, **kwargs) -> Response:
        """Сохраняем все cookies из redirect'a и сохраняем code авторизации из redirect_uri;
        
        Используем в дальнейшем в последующих запросах этой сессии.
        """
        response = super().request(method, self.base_url + url, **kwargs)
        if "register" not in url:
            for r in response.history:
                cookies = r.cookies.get_dict()
                self.cookies.update(cookies)
                code = parse_qs(urlparse(r.headers.get("Location")).query).get("code", None)
                if code:
                    self.code = code
        return response