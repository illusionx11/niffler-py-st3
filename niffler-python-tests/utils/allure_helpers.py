import allure
from requests import Response, JSONDecodeError
import curlify
import json
import requests

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
        from jinja2 import Environment, PackageLoader, select_autoescape
        method, url = args[1], args[2]
        env = Environment(
            loader=PackageLoader(package_name="schemas"),
            autoescape=select_autoescape()
        )
        template = env.get_template("http-colored-request.ftl")
        
        
        with allure.step(f"{method} {url}"):
            
            response: Response = function(*args, **kwargs)
            curl = curlify.to_curl(response.request)
            
            prepare_render = {
                "request": response.request,
                "curl": curl
            }
            render = template.render(prepare_render)
            
            allure.attach(
                body=render,
                name="Request",
                attachment_type=allure.attachment_type.HTML,
                extension=".html"
            )
            # logging.debug(curl)
            # logging.debug(response.text)

            try:
                allure.attach(
                    body=json.dumps(response.json(), indent=4).encode("utf-8"), 
                    name=f"Response json {response.status_code}", 
                    attachment_type=allure.attachment_type.JSON, 
                    extension=".html"
                )
            except (JSONDecodeError, TypeError):
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