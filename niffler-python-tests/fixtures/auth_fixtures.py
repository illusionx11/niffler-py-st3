import pytest
from models.config import ClientEnvs
from clients.oauth_client import OAuthClient
import logging
from pages.login_page import LoginPage
from pages.main_page import MainPage
import allure

@pytest.fixture(scope="session")
def auth_front_token(client_envs: ClientEnvs, login_page: LoginPage, main_page: MainPage):
    username = client_envs.test_username
    password = client_envs.test_password
    login_page.log_in(username, password)
    main_page.should_be_mainpage()
    token = main_page.get_access_token()
    allure.attach(token, name="front_token.txt", attachment_type=allure.attachment_type.TEXT)
    logging.info(token)
    return token

@pytest.fixture(scope="session", autouse=True)
def auth_api_token(client_envs: ClientEnvs, auth_client: OAuthClient):
    username = client_envs.test_username
    password = client_envs.test_password
    auth_client.register(username, password)
    token = auth_client.get_token(username, password)
    yield token