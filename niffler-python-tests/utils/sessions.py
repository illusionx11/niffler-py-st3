from requests import Session, Response
from urllib.parse import urlparse, parse_qs
from utils.allure_helpers import allure_attach_request, allure_attach_soap_request

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

class SoapSession(Session):
    """SOAP сессия для отправки raw XML запросов"""
    
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.base_url = kwargs.pop("base_url", "")
        self.headers.update({
            "Content-Type": "text/xml; charset=utf-8"
        })
    
    @allure_attach_soap_request
    def soap_request(self, xml_data: str) -> Response:
        """Отправка SOAP запроса с XML данными"""
        return self.post(self.base_url + "/ws", data=xml_data)